import pandas as pd
import time
import twstock
import requests
import json
from typing import Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from abc import abstractmethod

class TableDataBase():
    """Data type
    """
    def __init__(self) -> None:
        self.lose_val = False
        self.cheap = 0.0
        self.reasonable = 0.0
        self.expensive = 0.0
    
    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError("run not implement")


class RealTimePrice():
    """Get realtime price
    """
    def __init__(self) -> None:
        self.price_now = 0.0
        self.lose_val = False
        self.date=""
        self.time=""
    #改這
    def get_real_time_price(self, ticker) -> Dict[str, float | str]:
        """
        Fetch real-time price using the API and handle fallback if price is unavailable.

        Returns:
        A dictionary with price, date, and time.
        """
        # 組合完整的 URL
        stock_type = 'tse' if not ticker.startswith('6') else 'otc'
        query_url = f'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={stock_type}_{ticker}.tw'
        max_retries = 3 # 最大重试次数
        retries = 0

        while retries < max_retries:
            try:
                print(f"Fetching price for ticker {ticker}...")
                response = requests.get(query_url)
                if response.status_code != 200:
                    raise Exception('Failed to fetch stock info.')

                # 解析数据
                data = json.loads(response.text)
                stock_info = data['msgArray'][0]

                # 提取相关数据
                price = stock_info.get('z', '-')
                backup_price = stock_info.get('y', '0') # 昨收价格
                date = stock_info.get('d', '-') # 日期
                time = stock_info.get('t', '-') # 时间

                if price != '-' and price is not None:
                    self.price_now = round(float(price), 2)
                    self.lose_val = False
                    print(f"{date},{time},Price for ticker: {ticker} is: {self.price_now}.")
                    return {"price": self.price_now, "date": date, "time": time}

                print(f"Price unavailable for ticker {ticker}, retrying...")
                retries += 1
                time.sleep(8)

            except Exception as e:
                print(f"Error fetching price for ticker {ticker}: {e}, retrying...")
                self.lose_val = True
                retries += 1
                time.sleep(8)

                # 如果重试多次仍失败，返回昨收价格
        #print(f"Falling back to yesterday's price after {max_retries} retries.")
        self.price_now = round(float(backup_price), 2) if backup_price != '-' else 0.0
        #print("price", self.price_now, "date", date, "time", time)
        return {"price": self.price_now, "date": date, "time": time}



class CrawlerData():
    """Crawler data throw 
        https://goodinfo.tw/tw/StockBzPerformance.asp
    """
    def __init__(self, ticker) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("headless")
        s = Service(ChromeDriverManager().install())
        self.chrome = webdriver.Chrome(options = options, service = s)

        self.per_pbr = None
        self.dividend = None
        self.ticker = ticker

    def _get_dividend(self) -> None:
        self.chrome.get("https://goodinfo.tw/tw/StockBzPerformance.asp?STOCK_ID=%s"%(self.ticker))
        time.sleep(3)
        select_element = self.chrome.find_element(By.CSS_SELECTOR, "select#selSheet")  # Assuming ID is "selSheet"
        select_form = Select(select_element)
        select_form.select_by_index(3)
        time.sleep(3)

        form = self.chrome.find_element(by = By.ID, value = 'txtFinDetailData')
        self.dividend = pd.read_html(form.get_attribute('innerHTML'), header = 3)[0]
       
        for i in range(len(self.dividend)):
            if (self.dividend["股利 發放 年度"][i] == "股利 發放 年度" or self.dividend["股利 發放 年度"][i] == "股 利 政 策" or
                self.dividend["股利 發放 年度"][i] == "∟"):
                self.dividend.drop(i, inplace = True)

        self.dividend.reset_index(drop = True, inplace = True)
        
        
    def _get_per_pbr(self) -> None:
        self.chrome.get("https://goodinfo.tw/tw/StockBzPerformance.asp?STOCK_ID=%s"%(self.ticker))
        time.sleep(3)
        select_element = self.chrome.find_element(By.CSS_SELECTOR, "select#selSheet")  # Assuming ID is "selSheet"
        select_form = Select(select_element)
        select_form.select_by_index(2)
        time.sleep(3)

        form = self.chrome.find_element(by = By.ID, value = 'txtFinDetailData')
        self.per_pbr = pd.read_html(form.get_attribute('innerHTML'), header = 1)[0]

        for i in range(len(self.per_pbr)):
            if self.per_pbr["年度"][i] == "年度":
                self.per_pbr.drop(i, inplace = True)
        self.per_pbr.reset_index(drop = True, inplace = True)

    def get_data(self) -> None:
        self._get_per_pbr()
        self._get_dividend()


class Dividend(TableDataBase):
    def __init__(self, dividend_table : pd.DataFrame, year : str) -> None:
        super().__init__()
        self.dividend_table = dividend_table
        self.dividend = None
        self.dividend_table_json = None
        self.year = int(year)

    def run(self) -> None:

        self.dividend = self.dividend_table["股利 合計"][1:self.year+1]
        self.dividend.reset_index(drop = True, inplace = True)
    

        dividend_table_name = []
        dividend_table_name.append("ID")
        dividend_table_name.extend([str(x) for x in range(1, 8)])
        temp_dividend_table = self.dividend_table.drop(self.dividend_table.columns[8:], axis = 1)
        temp_dividend_table.drop(0, inplace = True)
        temp_dividend_table.drop(len(temp_dividend_table) - 1, inplace = True)
        temp_dividend_table.reset_index(drop = True, inplace = True)
        temp_dividend_table = temp_dividend_table.set_axis(dividend_table_name, axis = 1)
        self.dividend_table_json = temp_dividend_table[:self.year].to_dict(orient = 'records')
    


        if "-" in self.dividend.to_list():
            self.lose_val = True
        else:
            self.dividend = self.dividend.astype(float)
            dividend_avg = self.dividend.mean()

            self.cheap = round(dividend_avg * 15, 2)
            self.reasonable = round(dividend_avg * 20, 2)
            self.expensive = round(dividend_avg * 30, 2)


class Price(TableDataBase):
    def __init__(self, per_pbr_table : pd.DataFrame, year : str) -> None:
        super().__init__()
        self.price_table = per_pbr_table
        self.price_table_json = None
        self.price_high = None
        self.price_low = None
        self.price_avg = None
        self.year = int(year)

    def run(self):
        
        self.price_high = self.price_table["最高"][1:self.year+1]
        self.price_high.reset_index(drop = True, inplace = True)

        self.price_low = self.price_table["最低"][1:self.year+1]
        self.price_low.reset_index(drop = True, inplace = True)

        self.price_avg = self.price_table["平均"][1:self.year+1]
        self.price_avg.reset_index(drop = True, inplace = True)

        price_table_name = []
        price_table_name.append("ID")
        price_table_name.extend([str(x) for x in range(1, 5)])
        temp_price_table = self.price_table.drop(self.price_table.columns[7:], axis = 1)
        temp_price_table = temp_price_table.drop(temp_price_table.columns[1:3], axis = 1)
        temp_price_table.drop(0, inplace = True)
        temp_price_table.reset_index(drop = True, inplace = True)
        temp_price_table = temp_price_table.set_axis(price_table_name, axis = 1)
        self.price_table_json = temp_price_table[:self.year].to_dict(orient = 'records')

        if ("-" in self.price_high.to_list()) or ("-" in self.price_low.to_list()) or ("-" in self.price_avg.to_list()):
            self.lose_val = True
        else:
            self.price_high = self.price_high.astype(float)
            self.price_low = self.price_low.astype(float)
            self.price_avg = self.price_avg.astype(float)
            self.cheap = round(self.price_low.mean(), 2)
            self.reasonable = round(self.price_avg.mean(), 2)
            self.expensive = round(self.price_high.mean(), 2)

#本益比法
class Per(TableDataBase):
    def __init__(self, per_pbr_table : pd.DataFrame, year : str) -> None:
        super().__init__()
        self.PER_table = per_pbr_table
        self.PER_table_json = None
        self.PER_high = None
        self.PER_low = None
        self.PER_avg = None
        self.EPS = None
        self.year = int(year)
    
    def run(self):
        self.PER_high = self.PER_table["最高 PER"][1:self.year+1]
        self.PER_high.reset_index(drop = True, inplace = True)

        self.PER_low = self.PER_table["最低 PER"][1:self.year+1]
        self.PER_low.reset_index(drop = True, inplace = True)

        self.PER_avg = self.PER_table["平均 PER"][1:self.year+1]
        self.PER_avg.reset_index(drop = True, inplace = True)

        self.EPS = self.PER_table["EPS (元)"][1:self.year+1]
        self.EPS.reset_index(drop = True, inplace = True)

        PER_table_name = []
        PER_table_name.append("ID")
        PER_table_name.extend([str(x) for x in range(1, 5)])
        temp_PER_table = self.PER_table.drop(self.PER_table.columns[1:9], axis = 1)
        temp_PER_table = temp_PER_table.drop(temp_PER_table.columns[5:], axis = 1)
        temp_PER_table.drop(0, inplace = True)
        temp_PER_table.reset_index(drop = True, inplace = True)
        temp_PER_table = temp_PER_table.set_axis(PER_table_name, axis = 1)
        self.PER_table_json = temp_PER_table[:self.year].to_dict(orient = 'records')

        if (("-" in self.EPS.to_list()) or ("-" in self.PER_high.to_list()) or
            ("-" in self.PER_low.to_list()) or ("-" in self.PER_avg.to_list())):
            self.lose_val = True
        else:
                
            self.EPS = self.EPS.astype(float)
            self.PER_high = self.PER_high.astype(float)
            self.PER_low = self.PER_low.astype(float)
            self.PER_avg = self.PER_avg.astype(float)
            EPS_1year = self.EPS[0]
            EPS_xyear = self.EPS.mean()
            self.cheap = round(self.PER_low.mean() * ((EPS_1year + EPS_xyear) / 2), 2)
            self.reasonable = round(self.PER_avg.mean() * ((EPS_1year + EPS_xyear) / 2), 2)
            self.expensive = round(self.PER_high.mean() * ((EPS_1year + EPS_xyear) / 2), 2)

#本淨比法
class Pbr(TableDataBase):
    def __init__(self, per_pbr_table : pd.DataFrame, year : str) -> None:
        super().__init__()
        self.BPS = None
        self.BPS_now = 0.0
        self.PBR_table = per_pbr_table
        self.PBR_table_json = None
        self.PBR_high = None
        self.PBR_low = None
        self.PBR_avg = None
        self.year = int(year)
    
    def run(self) -> None:
        self.PBR_high = self.PBR_table["最高 PBR"][1:self.year+1]
        self.PBR_high.reset_index(drop = True, inplace = True)

        self.PBR_low = self.PBR_table["最低 PBR"][1:self.year+1]
        self.PBR_low.reset_index(drop = True, inplace = True)

        self.PBR_avg = self.PBR_table["平均 PBR"][1:self.year+1]
        self.PBR_avg.reset_index(drop = True, inplace = True)

        self.BPS = self.PBR_table["BPS (元)"][2:self.year+1]
        self.BPS_now = self.PBR_table["BPS (元)"][1]
        self.BPS.reset_index(drop = True, inplace = True)
        #print(self.PBR_table)
        PBR_table_name = []
        PBR_table_name.append("ID")
        PBR_table_name.extend([str(x) for x in range(1, 5)])
        temp_PBR_table = self.PBR_table.drop(self.PBR_table.columns[1:13], axis = 1)
        temp_PBR_table.drop(0, inplace = True)
        temp_PBR_table.reset_index(drop = True, inplace = True)
        temp_PBR_table = temp_PBR_table.set_axis(PBR_table_name, axis = 1)
        self.PBR_table_json = temp_PBR_table[:self.year].to_dict(orient = 'records')

        if ((self.BPS_now == "-") or ("-" in self.PBR_high.to_list()) or
            ("-" in self.PBR_low.to_list()) or ("-" in self.PBR_avg.to_list())):
            self.lose_val = True
        else:
            
            self.PBR_high = self.PBR_high.astype(float)
            self.PBR_low = self.PBR_low.astype(float)
            self.PBR_avg = self.PBR_avg.astype(float)
            self.BPS_now = float(self.BPS_now)
            self.cheap = round( self.PBR_low.mean() * self.BPS_now, 2)
            self.reasonable = round(self.PBR_avg.mean() * self.BPS_now, 2)
            self.expensive = round( self.PBR_high.mean() * self.BPS_now, 2)


class PricingStrategy():
    """Pricing strategy

        Args :
            ticker : (str) ticker
            year : (str) year
    """
    def __init__(self, ticker : str, year : str) -> None:
        self.ticker = ticker
        self.year = year
        self.RTP = RealTimePrice()
        self.CD = CrawlerData(ticker)

    def _handle_interval(self, result : Dict, strategy_object : object, max_value : float) -> None:
        """Handle result to bar type

            Args :
                result : (Dict) result
                strategy_object : (object) strategy object
                max_value : (float) max value

            Return:
                None
        """
        if(strategy_object.lose_val):
            result["down_cheap"].append(0.0)
            result["cheap_reasonable"].append(0.0)
            result["reasonable_expensive"].append(0.0)
            result["up_expensive"].append(0.0)
        else:
            result["down_cheap"].append(strategy_object.cheap)
            result["cheap_reasonable"].append(round(strategy_object.reasonable - strategy_object.cheap, 2))
            result["reasonable_expensive"].append(round(strategy_object.expensive - strategy_object.reasonable, 2))
            result["up_expensive"].append(round(max_value - strategy_object.expensive, 2))

    def run(self) -> Dict:
        """Run

            Args :
                None
            Return :
                Dict
        """
        
        # crawler data
        self.CD.get_data()
        
        # run different strategy
        dividend_strategy = Dividend(self.CD.dividend, self.year)
        price_strategy = Price(self.CD.per_pbr, self.year)
        per_strategy = Per(self.CD.per_pbr, self.year)
        pbr_strategy = Pbr(self.CD.per_pbr, self.year)

        dividend_strategy.run()
        price_strategy.run()
        per_strategy.run()
        pbr_strategy.run()
         


        result = {
            "NewPrice" : self.RTP.get_real_time_price(self.ticker),
            "down_cheap" : [],
            "cheap_reasonable" : [],
            "reasonable_expensive" : [],
            "up_expensive" : [],
            "cheap" : [dividend_strategy.cheap, price_strategy.cheap, per_strategy.cheap, pbr_strategy.cheap],
            "reasonable" : [dividend_strategy.reasonable, price_strategy.reasonable, per_strategy.reasonable, pbr_strategy.reasonable],
            "expensive" : [dividend_strategy.expensive, price_strategy.expensive, per_strategy.expensive, pbr_strategy.expensive],
            "Value lose" : [dividend_strategy.lose_val, price_strategy.lose_val, per_strategy.lose_val, pbr_strategy.lose_val, self.RTP.lose_val],
            "dividend_table" : { "data" : dividend_strategy.dividend_table_json },
            "high_low_table" : { "data" : price_strategy.price_table_json },
            "PER_table" : { "data" : per_strategy.PER_table_json },
            "PBR_table" : { "data" : pbr_strategy.PBR_table_json }
        }

        max_value = max(dividend_strategy.expensive, price_strategy.expensive, per_strategy.expensive, pbr_strategy.expensive) * 1.5

        self._handle_interval(result, dividend_strategy, max_value)
        self._handle_interval(result, price_strategy, max_value)
        self._handle_interval(result, per_strategy, max_value)
        self._handle_interval(result, pbr_strategy, max_value)
        #print("hw9:", result)
        print("this is new price",result['NewPrice'])
        return result

if __name__ == "__main__":
    ps = PricingStrategy("2330", 10)
    #print(ps.run()) 
    ps.run()