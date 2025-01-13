import pandas as pd
import time
import numpy as np
import datetime
import twstock
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from typing import Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

#logging.basicConfig(level=logging.DEBUG)

class PerRiver():
    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("headless")
        s = Service(ChromeDriverManager().install())
        self.chrome = webdriver.Chrome(options = options, service = s)

        self.data = {"data1" : [], "data2" : [], "data3" : [], "data4" : [], "data5" : [], "data6" : []}
        self.PER_rate_col = None
        self.EPS = 0.0
        self.realtime_price = 0.0

        self.kline = None

        self.evaluate = {"evaluate" : "", "cheap" : 0.0, "reasonable" : 0.0, "expensive" : 0.0}
    
    def _get_realtime_price(self, ticker : str) -> None:
        stock_info = twstock.realtime.get(ticker)
        bid = float(stock_info["realtime"]["best_bid_price"][-1])
        ask = float(stock_info["realtime"]["best_ask_price"][-1])

        price = (bid + ask) / 2
        self.realtime_price = round(price, 2)

    def _get_EPS(self, ticker: str, period: str) -> None:
        # 打開指定的 URL
        self.chrome.get(
            "https://goodinfo.tw/tw/ShowK_ChartFlow.asp?RPT_CAT=PER&STOCK_ID=%s&CHT_CAT=%s"
            % (ticker, period)
        )

        # 等待表格加載
        PER_River_form = WebDriverWait(self.chrome, 4).until(
            EC.presence_of_element_located((By.ID, "divDetail"))
        )

        # 讀取表格
        PER_table = pd.read_html(PER_River_form.get_attribute("innerHTML"), header=1)[0]

        # 提取 EPS 值
        self.EPS = float(PER_table[PER_table.columns[4]][0])

        # 刪除不需要的列，僅保留 "交易" 和數據列
        PER_table = PER_table.drop(
            PER_table.columns[[x for x in range(1, 6)]], axis=1
        )

        # 根據 period 確定時間戳記的列名
        time_column = {
            "MONTH": "交易 月份",
            "QUAR": "交易 季度",
            "YEAR": "交易 年度",
        }.get(period)

        if time_column not in PER_table.columns:
            raise ValueError(f"無法找到列名 '{time_column}'，請檢查數據結構。")

        # 處理時間戳記
        for i in range(len(PER_table)):
            raw_time = PER_table[time_column][i]  # 原始時間戳
            if raw_time == time_column:  # 忽略標題行
                PER_table.drop(i, inplace=True)
                continue

            # 根據 period 處理時間戳
            if period == "MONTH":  # 處理月份
                PER_table[time_column][i] = ("20" + raw_time).replace("M", "-") + "-01"
            elif period == "QUAR":  # 處理季度
                year = "20" + raw_time[:2]  # 提取年份
                quarter = raw_time[3]  # 提取季度
                start_month = (int(quarter) - 1) * 3 + 1  # 計算季度起始月份
                PER_table[time_column][i] = f"{year}-{start_month:02d}-01"
            elif period == "YEAR":  # 處理年份
                PER_table[time_column][i] = f"{raw_time}-01-01"

        # 重命名時間列名為統一名稱 "日期"
        PER_table.rename(columns={time_column: "日期"}, inplace=True)

        # 重設索引
        PER_table.reset_index(drop=True, inplace=True)

        # 填充 self.data
        for i in range(len(PER_table) - 1, -1, -1):
            for idx, key in enumerate(self.data.keys()):
                self.data[key].append([PER_table["日期"][i], PER_table[PER_table.columns[idx + 1]][i]])

        # 提取本益比列名稱
        self.PER_rate_col = PER_table.columns[1:].to_list()


        

    def _get_Kline(self, ticker: str, period: str) -> None:
        # 打開指定的 URL
        self.chrome.get(
            "https://goodinfo.tw/tw/ShowK_Chart.asp?STOCK_ID=%s&CHT_CAT=%s&PRICE_ADJ=F&SCROLL2Y=0"
            % (ticker, period)
        )

        # 等待表格加載
        KLine = WebDriverWait(self.chrome, 4).until(
            EC.presence_of_element_located((By.ID, "divDetail"))
        )

        # 讀取表格
        Kline_table = pd.read_html(KLine.get_attribute("innerHTML"), header=1)[0]

        # 刪除多餘的欄位，保留需要的部分
        Kline_table = Kline_table.drop(
            Kline_table.columns[[x for x in range(6, len(Kline_table.columns))]], axis=1
        )
        Kline_table = Kline_table.iloc[:-1]  # 刪除最後一行多餘的數據

        # 根據 period 確定時間戳記的列名
        time_column = {
            "MONTH": "交易 月份",
            "QUAR": "交易 季度",
            "YEAR": "交易 年度",
        }.get(period)

        if time_column not in Kline_table.columns:
            raise ValueError(f"無法找到列名 '{time_column}'，請檢查數據結構。")

        # 處理時間戳記
        for i in range(len(Kline_table)):
            raw_time = Kline_table[time_column][i]  # 原始時間戳
            if raw_time == time_column:  # 忽略標題行
                Kline_table.drop(i, inplace=True)
                continue

            # 根據 period 處理時間戳
            if period == "MONTH":  # 處理月份
                Kline_table[time_column][i] = ("20" + raw_time).replace("M", "-") + "-01"
            elif period == "QUAR":  # 處理季度
                year = "20" + raw_time[:2]  # 提取年份
                quarter = raw_time[3]  # 提取季度
                start_month = (int(quarter) - 1) * 3 + 1  # 計算季度起始月份
                Kline_table[time_column][i] = f"{year}-{start_month:02d}-01"
            elif period == "YEAR":  # 處理年份
                Kline_table[time_column][i] = f"{raw_time}-01-01"
        

        # 重命名時間列名為統一名稱 "日期"
        Kline_table.rename(columns={time_column: "日期"}, inplace=True)

        # 重設索引
        Kline_table.reset_index(drop=True, inplace=True)

        # 將表格數據存入 self.kline，反轉數據順序
        self.kline = Kline_table.values.tolist()
        self.kline.reverse()


    def _get_evaluate(self):
        self.evaluate["cheap"] = round(self.EPS * float(self.PER_rate_col[0][0:-1]), 2)
        self.evaluate["reasonable"] = round(self.EPS * ((float(self.PER_rate_col[2][0:-1]) + float(self.PER_rate_col[3][0:-1])) / 2), 2)
        self.evaluate["expensive"] = round(self.EPS * float(self.PER_rate_col[5][0:-1]), 2)

        if self.realtime_price <= self.evaluate["cheap"]:
            self.evaluate["evaluate"] = "評價: 目前價格(" + str(self.realtime_price) + ") < 便宜價(" + str(self.evaluate["cheap"]) + ")"
        
        elif ((self.realtime_price > self.evaluate["cheap"]) and
                (self.realtime_price <= self.evaluate["reasonable"])):
            self.evaluate["evaluate"] = "評價: 便宜價(" + str(self.evaluate["cheap"]) + ")" + "< 目前價格(" + str(self.realtime_price) + ") < 合理價("+ str(self.evaluate["reasonable"]) + ")"
        
        elif ((self.realtime_price > self.evaluate["reasonable"]) and
                (self.realtime_price <= self.evaluate["expensive"])):
            self.evaluate["evaluate"] = "評價: 合理價(" + str(self.evaluate["reasonable"]) + ")" + "< 目前價格(" + str(self.realtime_price) + ") < 昂貴價(" + str(self.evaluate["expensive"]) + ")"
        
        else:
            self.evaluate["evaluate"] = "評價: 目前價格(" + str(self.realtime_price) + ") > 昂貴價(" + str(self.evaluate["expensive"]) + ")"

    def run(self, ticker : str, period : str) -> Dict:
        """Run

            Args :
                ticker : (str) ticker
                period : (str) interval
                
            Return:
                Dict
        """
        self._get_realtime_price(ticker)
        self._get_EPS(ticker, period)
        self._get_Kline(ticker, period)
        self._get_evaluate()
        
        result = {
            "NewPrice" : self.realtime_price,
            "PER_rate" : self.PER_rate_col,
            "EPS" : self.EPS,
            "Kline" : self.kline,
            "data1" : self.data["data1"],
            "data2" : self.data["data2"],
            "data3" : self.data["data3"],
            "data4" : self.data["data4"],
            "data5" : self.data["data5"],
            "data6" : self.data["data6"],
            "cheap" : self.evaluate["cheap"],
            "reasonable" : self.evaluate["reasonable"],
            "expensive" : self.evaluate["expensive"],
            "evaluate" : self.evaluate["evaluate"],
            "down_cheap" : [self.evaluate["cheap"]],
            "cheap_reasonable" : [round(self.evaluate["reasonable"] - self.evaluate["cheap"], 2)],
            "reasonable_expensive" : [round(self.evaluate["expensive"] - self.evaluate["reasonable"], 2)],
            "up_expensive" : [round(self.evaluate["expensive"] * 1.5 - self.evaluate["expensive"], 2)]
        }
        
        df_data1 = pd.DataFrame(result['data1'], columns=["Date", "Value"])
        
        data1_str = df_data1["Date"].astype(str)

        data1_result_list = []
        
        for date_str in data1_str:
            date_str = date_str.split(' ')[0]
            timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
            data1_result_list.append(timestamp)
            
        df_data1.reset_index(inplace=True)
            
        list_data1 = df_data1['Value'].tolist()
 
        combined_list_data1 = [[date, k] for date, k in zip(data1_result_list, list_data1)]

        # combined_list = [[date, adj_close] for date, adj_close in zip(result_list, list_K, list_D)]
        
        # 列表 轉成 NumPy 数组
        combined_array_data1 = np.array(combined_list_data1)

        data_stock_data1 = combined_array_data1.tolist()
        
        print(data_stock_data1)
        #print('result 1~6 as below:')

        # print(result['data1'])
        # print(result['data2'])
        # print(result['data3'])
        # print(result['data4'])
        # print(result['data5'])
        # print(result['data6'])

        return result

if __name__ == "__main__":
    per = PerRiver()
    print(per.run("2330", "MONTH"))
    
    
    
#以LOC處理時間戳
# def process_time_stamp(raw_time, period):
#     if period == "MONTH":
#         return ("20" + raw_time).replace("M", "-") + "-01"
#     elif period == "QUAR":
#         year = "20" + raw_time[:2]
#         quarter = raw_time[3]
#         start_month = (int(quarter) - 1) * 3 + 1
#         return f"{year}-{start_month:02d}-01"
#     elif period == "YEAR":
#         return f"{raw_time}-01-01"
#     else:
#         raise ValueError("Unknown period format")

# # 處理時間戳記
# Kline_table[time_column] = Kline_table[time_column].apply(lambda x: process_time_stamp(x, period) if x != time_column else None)
# Kline_table.dropna(subset=[time_column], inplace=True)