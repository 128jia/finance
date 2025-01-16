from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse #匯入http模組
from datetime import datetime
import datetime
import yfinance as yf
import pandas as pd
from django.http import JsonResponse
import time
import talib
from talib import abstract
import numpy as np
import json
from collections import defaultdict
from django.contrib import messages
import copy
import backtrader as bt
from web_tool.models import StrategyResult
import traceback  # 用於打印完整的錯誤追踪
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import math
import logging

# def web(request):
#     if not request.user.is_authenticated:
#         messages.success(request, 'Sorry ! Please Log In.')
#         return redirect("http://127.0.0.1:8081/account/login")
#     return (render(request,"base.html"))


def index(request):

  
    # if not request.user.is_authenticated:
    #     messages.success(request, 'Sorry ! Please Log In.')
    #     return redirect("http://127.0.0.1:1984/account/login")
    return render(request, 'index.html', locals())

def stock(stock_name, start_day, end_day):
    
    data_stock   = yf.download(stock_name, start_day, end_day)
    
    # 注意：yfinance 下载的数据中 Date 是索引，需要重置索引
    data_stock.reset_index(inplace=True)
    
    data_stock   = data_stock[['Date', 'Adj Close']]
    date_strings = data_stock['Date'].astype(str)
    date_list    = []
    
    for date_str in date_strings:
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        date_list.append(timestamp)
    adj_close_list = data_stock['Adj Close'].tolist()
    combined_list  = [[date, adj_close] for date, adj_close in zip(date_list, adj_close_list)]

    # 列表 轉成 NumPy 数组
    combined_array = np.array(combined_list)

    data_stock     = combined_array.tolist()

    return data_stock

def load(stock_name, sub_stock_name, start_day, end_day):
    
    #圖一
    trading_signals = defaultdict(list)
    spread = None  
    rolling_mean = None
    rolling_std = None  
    upper_line = None
    lower_line = None
    upper_status = 0
    lower_status = 0
    close_prices = {}
    #圖二
    exe_trading_signals = None
    profit_loss_val = 0
    oper_value = 10000
    daily_profits = []
    total_values = []
    entry_point = []
    exit_point = []

    # -----------------------------------------------------------------------------------------第一張圖(三角)開始-----------------------------------------------------------------------------------------
    #下載數據
    data1 = yf.download(stock_name, start_day, end_day)
    data2 = yf.download(sub_stock_name, start_day, end_day)
    close_prices[stock_name] = data1['Adj Close']
    close_prices[sub_stock_name] = data2['Adj Close']
        
    normalized_price1 = pd.Series(np.log(close_prices[stock_name]))
    normalized_price2 = pd.Series(np.log(close_prices[sub_stock_name]))  
    
    # 將兩組標準化後的數組相減並計算移動標準差與移動平均值
    spread = normalized_price1 - normalized_price2    #算出spread
    rolling_mean = spread.rolling(window=200).mean()
    rolling_std = spread.rolling(window=200).std() 
    upper_line = rolling_mean + 2 * rolling_std
    lower_line = rolling_mean - 2 * rolling_std

    trading_signals = defaultdict(list)
    for ind, val in enumerate(spread):
        
        if np.isnan(float(val)):
            continue
        
        date = spread.index[ind]
        target_spread = spread[ind]  
        
        adj_close_stock = close_prices[stock_name].loc[date]  # 主股票的调整后收盘价
        adj_close_sub_stock = close_prices[sub_stock_name].loc[date]  # 次股票的调整后收盘价

        
        if target_spread >= upper_line[ind] and (upper_status == 0):
            trading_signals[f'upper'].append([date, target_spread, 'SELL', "Open", adj_close_stock, adj_close_sub_stock])
            upper_status = 1

        if target_spread <= rolling_mean[ind] and (upper_status == 1):
            trading_signals[f'upper'].append([date, target_spread, 'BUY', "Close", adj_close_stock, adj_close_sub_stock])
            upper_status = 0


        if target_spread <= lower_line[ind] and (lower_status == 0):
            trading_signals[f'lower'].append([date, target_spread, 'BUY', "Open", adj_close_stock, adj_close_sub_stock])
            lower_status = 1

        if target_spread >= rolling_mean[ind] and (lower_status == 1):
            trading_signals[f'lower'].append([date, target_spread, 'SELL', "Close", adj_close_stock, adj_close_sub_stock])
            lower_status = 0

    # print('trading_signals:',trading_signals)
    # 轉成普通字典
    trading_signals_dict = dict(trading_signals)

    #去掉 defaultdict 和 np.float64()
    data = {
        key: [
            [
                int(values[0].timestamp()),  # 转换为时间戳
                float(values[1]) if isinstance(values[1], np.float64) else values[1],  # 检查并转换
                values[2],  # 直接获取 'SELL' 或 'BUY'
                values[3],  # 直接获取 'Open' 或 'Close'
                float(values[4]) if isinstance(values[4], np.float64) else values[4],  # 检查并转换
                float(values[5]) if isinstance(values[5], np.float64) else values[5]   # 检查并转换
            ]
            for values in trading_signals_dict[key]  # 遍历每个值列表
        ]
        for key in trading_signals_dict  # 遍历字典的每个键
    }
    
    for category in data:
        for entry in data[category]:
            entry[0] *= 1000
    
    
    upper = data['upper']
    lower = data['lower']
    


    stock_name_red       = [(item[0], item[4]) for item in upper if item[3] == 'Open' ] + [(item[0], item[4]) for item in lower if item[3] == 'Close']
    stock_name_green     = [(item[0], item[4]) for item in upper if item[3] == 'Close'] + [(item[0], item[4]) for item in lower if item[3] == 'Open' ]
    sub_stock_name_red   = [(item[0], item[5]) for item in upper if item[3] == 'Close'] + [(item[0], item[5]) for item in lower if item[3] == 'Open' ]
    sub_stock_name_green = [(item[0], item[5]) for item in upper if item[3] == 'Open' ] + [(item[0], item[5]) for item in lower if item[3] == 'Close']


    # print('data',data)
    # print(upper)
    # print(lower)
    # -----------------------------------------------------------------------------------------第一張圖(三角)結束-----------------------------------------------------------------------------------------
    
    # -----------------------------------------------------------------------------------------第二張圖(損益)開始-----------------------------------------------------------------------------------------
    
    # 計算實際交易日
    tmp_result = []
    unique_trades = set()
    for trade in [item for sublist in trading_signals.values() for item in sublist]:
        trade_tuple = tuple(trade[1:])
        if trade_tuple not in unique_trades:
            tmp_result.append(copy.deepcopy(trade))
            unique_trades.add(trade_tuple)
            
    exe_trading_signals = sorted(tmp_result, key=lambda x: x[0])
    
    for ele in exe_trading_signals:
        date = ele[0]
        next_date = close_prices[stock_name].index[close_prices[stock_name].index.get_loc(date) + 1]  
        ele[0] = next_date       
        
    #初始變量設定
    all_qty1 = 0
    all_qty2 = 0
    qty1 = 0
    qty2 = 0
    stock1_type = None
    stock2_type = None
    
    for ind, val in enumerate(close_prices[stock_name]):
        date = close_prices[stock_name].index[ind]
        price1 = close_prices[stock_name][ind]
        price2 = close_prices[sub_stock_name][ind]
        daily_profit = 0

        # 檢查是否有開倉信號
        matching_entry = list(filter(lambda x: x[0] == date and x[3] == 'Open', exe_trading_signals))
        if matching_entry:
            qty1 = (oper_value / 2) / price1
            qty2 = (oper_value / 2) / price2

            if stock1_type == "BUY" and stock2_type == "SELL":
                daily_profit = (all_qty1 * price1) - (all_qty2 * price2)
            elif stock1_type == "SELL" and stock2_type == "BUY":
                daily_profit = -(all_qty1 * price1) + (all_qty2 * price2)
            
            if matching_entry[0][2] == "BUY":
                entry_profit = -(qty1 * price1) + (qty2 * price2)
                stock1_type = "BUY"
                stock2_type = "SELL"
            elif matching_entry[0][2] == "SELL":
                entry_profit = (qty1 * price1) - (qty2 * price2)
                stock1_type = "SELL"
                stock2_type = "BUY"
            profit_loss_val += entry_profit

            all_qty1 += qty1
            all_qty2 += qty2
            
            # 計算當前總收益百分比
            entry_percentage = ((profit_loss_val+daily_profit) / oper_value) * 100
            entry_point.append((date, entry_percentage))
        
        # 檢查是否有平倉信號
        matching_exits = list(filter(lambda x: x[0] == date and x[3] == 'Close', exe_trading_signals))
        if matching_exits:
            if matching_exits[0][2] == "BUY":
                daily_profit = -(all_qty1 * price1) + (all_qty2 * price2)
            elif matching_exits[0][2] == "SELL":
                daily_profit = (all_qty1 * price1) - (all_qty2 * price2)
        
            profit_loss_val += daily_profit
            
            # 計算當前總收益百分比
            exit_percentage = (profit_loss_val / oper_value) * 100
            exit_point.append((date, exit_percentage))
            
            # initialize
            all_qty1 = 0
            all_qty2 = 0
            stock1_type = None
            stock2_type = None
            
        # 根據持有的倉位記錄每日的獲利
        if not matching_exits and not matching_entry:
            if stock1_type == "BUY" and stock2_type == "SELL":
                daily_profit = (all_qty1 * price1) - (all_qty2 * price2)
            elif stock1_type == "SELL" and stock2_type == "BUY":
                daily_profit = -(all_qty1 * price1) + (all_qty2 * price2)
            
            # 計算當前總收益百分比
            daily_percentage = ((profit_loss_val + daily_profit) / oper_value) * 100
            daily_profits.append((date, daily_percentage))

        # 記錄總值百分比
        total_percentage = (profit_loss_val / oper_value) * 100
        total_values.append((date, total_percentage))
        
    pl_daily_profits = [[int(date.timestamp() * 1000), val] for date, val in daily_profits]
    pl_total_values  = [[int(date.timestamp() * 1000), val] for date, val in total_values ]
    pl_entry_point   = [[int(date.timestamp() * 1000), val] for date, val in entry_point  ]
    pl_exit_point    = [[int(date.timestamp() * 1000), val] for date, val in exit_point   ]
    
    # -----------------------------------------------------------------------------------------第二張圖(損益)結束-------------------------------------------------------------------------------------------
    
    # -----------------------------------------------------------------------------------------第三張圖(布林帶)開始-----------------------------------------------------------------------------------------
    
    sorted_list        = sorted((trading_signals['upper'] + trading_signals['lower']), key=lambda x: x[0])
    spread             = spread.dropna()
    spread             = spread.reset_index()
    spread             = spread.values.tolist()
    spread             = [[int(date.timestamp() * 1000), val] for date, val in spread]
    middle_line        = rolling_mean.dropna()
    middle_line        = middle_line.reset_index()
    middle_line        = middle_line.values.tolist()
    middle_line        = [[int(date.timestamp() * 1000), val] for date, val in middle_line]
    upper_line         = upper_line.dropna()
    upper_line         = upper_line.reset_index()
    upper_line         = upper_line.values.tolist()
    upper_line         = [[int(date.timestamp() * 1000), val] for date, val in upper_line]
    lower_line         = lower_line.dropna()
    lower_line         = lower_line.reset_index()
    lower_line         = lower_line.values.tolist()
    lower_line         = [[int(date.timestamp() * 1000), val] for date, val in lower_line]
    bands_signals_sell = [[int(ele[0].timestamp() * 1000), ele[1]] for ele in sorted_list if ele[2]=='SELL']
    bands_signals_buy  = [[int(ele[0].timestamp() * 1000) , ele[1]] for ele in sorted_list if ele[2]=='BUY']
    
    # -----------------------------------------------------------------------------------------第三張圖(布林帶)結束-----------------------------------------------------------------------------------------
    
    # -----------------------------------------------------------------------------------------  DataTable1  開始-----------------------------------------------------------------------------------------
    
    # stock price data
    all_price = pd.DataFrame({
        'date': data1.index,
        stock_name: data1['Close'],
        sub_stock_name: data2['Close']
    })
    
    sorted_list = sorted((trading_signals['upper'] + trading_signals['lower']), key=lambda x: x[0])
    
    table_signals = []
    for row in sorted_list:
        stock1_price1 = round(all_price.loc[row[0].strftime("%Y-%m-%d"), stock_name], 2)
        stock2_price1 = round(all_price.loc[row[0].strftime("%Y-%m-%d"), sub_stock_name], 2)     
        if row[2]=="BUY":
            table_signals.append({"date":row[0], "stock_name_action": "BUY", "stock_name_price":stock1_price1, "sub_stock_name_action":"SELL", "sub_stock_name_price":stock2_price1, "type":row[3]})
        elif row[2]=="SELL":
            table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock_name_action":"SELL", "stock_name_price":stock1_price1, "sub_stock_name_action":"BUY", "sub_stock_name_price":stock2_price1, "type":row[3]})

    # -----------------------------------------------------------------------------------------  DataTable1  結束-----------------------------------------------------------------------------------------
    
    # -----------------------------------------------------------------------------------------  DataTable2  開始-----------------------------------------------------------------------------------------
    
     
    exit_date = [ele[0] for ele in copy.deepcopy(exit_point)]    
    tmp_data = [item[1] for item in copy.deepcopy(total_values) if item[0] in exit_date]
    percentage = []
    # print(tmp_data)
    for i in range(0, len(tmp_data)):
        if i != 0:
            subtraction = tmp_data[i] - tmp_data[(i-1)]
        else:
            subtraction = tmp_data[i]
        percentage.append(round(subtraction,2))
    
    n=0
    exe_table_signals = []
    for row in exe_trading_signals:
        stock1_price1 = round(all_price.loc[row[0].strftime("%Y-%m-%d"), stock_name], 2)
        stock2_price1 = round(all_price.loc[row[0].strftime("%Y-%m-%d"), sub_stock_name], 2)     
        if row[2]=="BUY":
            if row[3] =="Open":
                exe_table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock_name_action": "BUY", "stock_name_price":stock1_price1, "sub_stock_name_action":"SELL", "sub_stock_name_price":stock2_price1, "type":row[3], "percentage": None})
            else:
                exe_table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock_name_action": "BUY", "stock_name_price":stock1_price1, "sub_stock_name_action":"SELL", "sub_stock_name_price":stock2_price1, "type":row[3], "percentage": percentage[n]})
                n+=1
        elif row[2]=="SELL":
            if row[3] =="Open":
                exe_table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock_name_action":"SELL", "stock_name_price":stock1_price1, "sub_stock_name_action":"BUY", "sub_stock_name_price":stock2_price1, "type":row[3], "percentage": None})
            else:
                exe_table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock_name_action": "BUY", "stock_name_price":stock1_price1, "sub_stock_name_action":"SELL", "sub_stock_name_price":stock2_price1, "type":row[3], "percentage": percentage[n]})
                n+=1
    
    return (stock_name_red, stock_name_green, sub_stock_name_red, sub_stock_name_green, 
            pl_daily_profits, pl_total_values, pl_entry_point, pl_exit_point, 
            spread, upper_line, middle_line, lower_line, bands_signals_sell, bands_signals_buy,
            table_signals, exe_table_signals)

def ajax_data(request):
    if request.method == 'POST':
        # action = request.POST.get('action', '')
        # if action == 'search_stock':
            # print('in ajax_data')
        try:
            # request.POST.get('start_date')
            stock_name     = request.POST.get('stock1')
            # sub_stock_name = request.POST.get('sub_name'  )
            start_date     = request.POST.get('start_date')
            end_date       = request.POST.get('end_date')
            fastk_period   = request.POST.get('fastk_period')
            slowk_period   = request.POST.get('slowk_period')
            slowd_period   = request.POST.get('slowd_period')
            fastperiod     = request.POST.get('fastperiod')
            slowperiod     = request.POST.get('slowperiod')
            signalperiod   = request.POST.get('signalperiod')
            bb_timeperiod  = request.POST.get('bb_timeperiod')
            nbdevup        = request.POST.get('nbdevup')
            nbdevdn        = request.POST.get('nbdevdn')
            matype         = request.POST.get('matype')
            rsi_timeperiod = request.POST.get('rsi_timeperiod')
            dmi_timeperiod = request.POST.get('dmi_timeperiod')
                       
            # 換整數
            fastk_period = int(fastk_period)
            slowk_period = int(slowk_period)
            slowd_period = int(slowd_period)
            fastperiod = int(fastperiod)
            slowperiod = int(slowperiod)
            signalperiod = int(signalperiod)
            bb_timeperiod = int(bb_timeperiod)
            nbdevup = int(nbdevup)
            nbdevdn = int(nbdevdn)
            matype = int(matype)
            rsi_timeperiod = int(rsi_timeperiod)
            dmi_timeperiod = int(dmi_timeperiod)
                        
            response = inductor_tra(
                stock_name, start_date, end_date, 
                fastk_period, slowk_period, slowd_period, 
                fastperiod, slowperiod, signalperiod,
                bb_timeperiod, nbdevup, nbdevdn, matype,
                rsi_timeperiod, dmi_timeperiod
            )

            
            '''
            原來不用API的method
            
            start_day = datetime.strptime(start_day, "%Y/%m/%d")
            # 将 datetime 对象转换为新的字符串格式
            start_day = start_day.strftime("%Y-%m-%d")
            
            end_day = datetime.strptime(end_day, "%Y/%m/%d")
            # 将 datetime 对象转换为新的字符串格式
            end_day = end_day.strftime("%Y-%m-%d")
            
            print(start_day)
            print(end_day)
            
            message = stock(stock_name, start_day, end_day)
            sub_message = stock(sub_stock_name, start_day, end_day)
            # message = stock(stock_name)
            # sub_message = stock(sub_stock_name)
            
            (
            stock_name_red, stock_name_green, sub_stock_name_red, sub_stock_name_green, 
            pl_daily_profits, pl_total_values, pl_entry_point, pl_exit_point, 
            spread, upper_line, middle_line, lower_line, bands_signals_sell, bands_signals_buy,
            table_signals,exe_table_signals
            ) = load(stock_name, sub_stock_name, start_day, end_day)    
            
            response = {
                'data_stock'          : [message,sub_message]       ,
                'stock_name'          : [stock_name,sub_stock_name] ,
                'stock_name_red'      : stock_name_red              ,
                'stock_name_green'    : stock_name_green            ,
                'sub_stock_name_red'  : sub_stock_name_red          ,
                'sub_stock_name_green': sub_stock_name_green        ,
                'pl_daily_profits'    : pl_daily_profits            ,
                'pl_total_values'     : pl_total_values             ,
                'pl_entry_point'      : pl_entry_point              ,
                'pl_exit_point'       : pl_exit_point               ,
                'spread'              : spread                      ,
                'middle_line'         : middle_line                 ,
                'upper_line'          : upper_line                  ,
                'lower_line'          : lower_line                  ,
                'bands_signals_sell'  : bands_signals_sell          ,
                'bands_signals_buy'   : bands_signals_buy           ,
                'table_signals'       : table_signals               ,
                'exe_table_signals'   : exe_table_signals           ,
            }
            '''
            
            '''
            # ic
            # # ------ API ------
            # # Communicate with function api
            # from common.func_client import FuncClient
            
            # #实例化 FuncClient 对象，赋值给 fc,fc 实例将用于调用 FuncClient 中的方法
            # fc = FuncClient()
            
            # #包含配对交易回测所需参数的字典
            # params = {
            #     'stock_name' : str(stock_name),
            #     # 'sub_stock_name' : str(sub_stock_name),
            #     'start_day' : str(start_day),
            #     'end_day' : str(end_day),
            #     # 'window_size' : int(window_sizes),
            #     # 'n_times' : int(std)
            # }
            
            # #通过 fc 对象调用 pairtrading_backtesting 方法，并传入 params 字典作为参数，指定 method 为 "distance"。pairtrading_backtesting 执行配对交易的回测逻辑，并返回结果 res。
            # res = fc.pairtrading_backtesting(params=params, method="distance")
            
            # print(res['bands_signals_sell'])
            # print(res['bands_signals_buy'])
            
            # response = {
            #     'data_stock'          : [res['message'],res['sub_message']],
            #     # 'stock_name'          : [stock_name,sub_stock_name]        ,
            #     'stock_name_red'      : res['stock_name_red']              ,
            #     'stock_name_green'    : res['stock_name_green']            ,
            #     'sub_stock_name_red'  : res['sub_stock_name_red']          ,
            #     'sub_stock_name_green': res['sub_stock_name_green']        ,
            #     'pl_daily_profits'    : res['pl_daily_profits']            ,
            #     'pl_total_values'     : res['pl_total_values']             ,
            #     'pl_entry_point'      : res['pl_entry_point']              ,
            #     'pl_exit_point'       : res['pl_exit_point']               ,
            #     'spread'              : res['spread']                      ,
            #     'middle_line'         : res['middle_line']                 ,
            #     'upper_line'          : res['upper_line']                  ,
            #     'lower_line'          : res['lower_line']                  ,
            #     'bands_signals_sell'  : res['bands_signals_sell']          ,
            #     'bands_signals_buy'   : res['bands_signals_buy']           ,
            #     'table_signals'       : res['table_signals']               ,
            #     'exe_table_signals'   : res['exe_table_signals']           ,
            # }
            '''

            return JsonResponse(response, safe=False)            
        except:
            message = 'Something wrong, please check again.'
            return JsonResponse(message, safe=False)
        # else:
        #     return JsonResponse({'message': 'Invalid action.'})
        
    return JsonResponse({'message': 'Invalid request method.'})


def inductor(request):
    if request.method == 'POST':
        print('inductor post')
        try:
            print('inductor backend')
            stock_inductor = request.POST.get('stock_inductor')
            start_date_inductor = request.POST.get('start_date_inductor')
            end_date_inductor = request.POST.get('end_date_inductor')
            day = request.POST.get('day')
            day = int(day)
            
            # ----------------------------------- 爆大量,五日均線,量值,蠟燭圖---------------------------------------------------------------------------------------------------------

            data_stock_HighVolume, data_stock_df_vol, data_stock_vol_df_5dayvol, data_stock_candle_d_day = cal_d_day_sma(
                                                                                                                        stock_inductor, start_date_inductor, 
                                                                                                                        end_date_inductor, day
                                                                                                                        )
            

            response = {
                'data_stock_HighVolume'     : data_stock_HighVolume,
                'data_stock_vol_df_5dayvol' : data_stock_vol_df_5dayvol,
                'data_stock_df_vol'         : data_stock_df_vol,
                'data_stock_candle_d_day'   : data_stock_candle_d_day
            }
                            
            return JsonResponse(response, safe=False)            
        except:
            message = 'Inductor views.py.inductor wrong, please check again.'
            return JsonResponse(message, safe=False)
    return JsonResponse({'message': 'Invalid views.py.inductor request method.'})

# d日量能均線 ---------- start ----------

# yfinance抓資料
def fetch_stock_data(stock_symbol, start_date, end_date):
    
    print('in fetch_stock_data')
    """
    使用 yfinance 抓取開高低收和量能數據
    """
    df = pd.DataFrame(yf.download(stock_symbol, start=start_date, end=end_date))
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    return df

# 找五日均線
def calculate_5day_avg_volume_talib(df, day):
    """
    使用 TA-Lib 計算量能的5日均线
    """
    print('in calculate_5day_avg_volume_talib')
    df['5DayAvgVolume'] = talib.SMA(df['Volume'], timeperiod=day)
    vol_df = df.dropna()

    return vol_df

# 找爆大量
def find_high_volume_days(df):
    print('in find_high_volume_days')
    """
    找出爆大量的日期，并返回一个新的 DataFrame
    條件：當日量能 > 5日均量
    """
    high_volume_days = df[df['Volume'] > df['5DayAvgVolume']][['Volume']]  # 篩選出爆大量的行
    high_volume_days = high_volume_days.reset_index()  # 重置索引以保留日期列
    high_volume_days = high_volume_days.rename(columns={'index': 'Date', 'Volume': 'HighVolume'})  # 重命名列名

    return high_volume_days

# 計算數值處理完傳回前端
def cal_d_day_sma(stock_symbol, start_date, end_date, day):

    # 1. 抓取開、高、低、收、量能
    print('in cal_d_day_sma')
    df = fetch_stock_data(stock_symbol, start_date, end_date)

    # 2. 使用 TA-Lib 計算量能的5日均線
    vol_df = calculate_5day_avg_volume_talib(df, day)

    # 3. 找出爆大量的日期
    high_volume_days_df = find_high_volume_days(df)
    
    print('all function OK!')
    
    # ANS
    
    # 1.資料處理-爆大量天數-日期和量能
    high_volume_days_df.reset_index(inplace=True)
    high_volume_days_date = high_volume_days_df[['Date', 'HighVolume']]
    high_volume_days_date_str = high_volume_days_date["Date"].astype(str)
    
    high_vol_result_list = []

    for date_str in high_volume_days_date_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        # timestamp = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp()) * 1000
        timestamp += 24 * 60 * 60 * 1000 * 2
        high_vol_result_list.append(timestamp)

    list_HighVolume = high_volume_days_df['HighVolume'].tolist()

    combined_list_HighVolume = [[date, hv] for date, hv in zip(high_vol_result_list, list_HighVolume)]

    combined_array_HighVolume = np.array(combined_list_HighVolume)

    data_stock_HighVolume = combined_array_HighVolume.tolist()
    
    print('data_stock_HighVolume : ', data_stock_HighVolume)
    # 資料處理-爆大量天數-日期和量能
    
    # 2.d日均線圖
    
    vol_df.reset_index(inplace=True)
    vol_df_sma_date = vol_df[['Date', '5DayAvgVolume']]
    vol_df_sma_date_str = vol_df_sma_date["Date"].astype(str)
    vol_df_sma_result_list = []

    for date_str in vol_df_sma_date_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        timestamp += 24 * 60 * 60 * 1000 * 2
        vol_df_sma_result_list.append(timestamp)

    list_vol_df_5dayvol = vol_df['5DayAvgVolume'].tolist()

    combined_list_vol_df_5dayvol = [[date, dayAvg] for date, dayAvg in zip(vol_df_sma_result_list, list_vol_df_5dayvol)]

    combined_array_vol_df_5dayvol = np.array(combined_list_vol_df_5dayvol)

    data_stock_vol_df_5dayvol = combined_array_vol_df_5dayvol.tolist()
    
    # d日均線圖
    # 3.量值&蠟燭圖開高低收 + 日期 

    df.reset_index(inplace=True)
    df_vol_date = df[['Date', 'Volume', 'Open', 'High', 'Low', 'Close']]
    df_vol_date_str = df_vol_date["Date"].astype(str)
    df_vol_result_list = []

    for date_str in df_vol_date_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        # timestamp = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp()) * 1000
        timestamp += 24 * 60 * 60 * 1000 * 2
        df_vol_result_list.append(timestamp)

    list_df_vol = df['Volume'].tolist()
    list_open   = df['Open'].tolist()
    list_high   = df['High'].tolist()
    list_low    = df['Low'].tolist()
    list_close  = df['Close'].tolist()

    combined_list_df_vol = [[date, vol] for date, vol in zip(df_vol_result_list, list_df_vol)]
    combined_list_candle = [[date, open, high, low, close] for date, open, high, low, close in zip(df_vol_result_list, list_open, list_high, list_low, list_close)]
    
    combined_array_df_vol = np.array(combined_list_df_vol)
    combined_array_candle = np.array(combined_list_candle) 

    data_stock_df_vol = combined_array_df_vol.tolist()
    data_stock_candle_d_day = combined_array_candle.tolist()
    
    return data_stock_HighVolume, data_stock_df_vol, data_stock_vol_df_5dayvol, data_stock_candle_d_day

    # d日量能均線 ---------- end ----------











































# 黃金交叉
def crossover(over, down):
    a1 = over
    b1 = down
    a2 = a1.shift(1)
    b2 = b1.shift(1)
    crossover = (a1 > a2) & (a1 > b1) & (b2 > a2)
    return crossover

# 死亡交叉
def crossunder(down, over):
    a1 = down
    b1 = over
    a2 = a1.shift(1)
    b2 = b1.shift(1)
    crossdown = (a1 < a2) & (a1 < b1) & (b2 < a2)
    return crossdown

# RSI指標
def rsi(stock_inductor, start_date_inductor, end_date_inductor):
    
    df=pd.DataFrame(yf.download(stock_inductor, start_date_inductor, end_date_inductor))
    
    # 将所有列名转换为小写
    df.columns = [col.lower() for col in df.columns]
    
    # print(df.columns)

    # 計算 RSI、ADX 
    df["ADX"] = abstract.ADX(df, timeperiod = 14)
    df["RSI"] = abstract.RSI(df, timeperiod = 20)
    
    # print('here', df['close'])
    
    # ------
    
    # 計算DMI
    high = df['high']
    low = df['low']
    close = df['close']
    # 計算 +DI, -DI 和 ADX
    period = 14  # 通常的周期是 14
    df["DIP"] = talib.PLUS_DI(high, low, close, timeperiod=period)
    df["DIM"] = talib.MINUS_DI(high, low, close, timeperiod=period)
    
    # ------


    # 删除包含 NaN 的行
    df.dropna(subset=["RSI"], inplace=True)
    df.dropna(subset=["ADX"], inplace=True)
    df.dropna(subset=["DIP"], inplace=True)
    df.dropna(subset=["DIM"], inplace=True)

    # DMI金叉死叉
    df["DMI_Golden_Cross"] = crossover(df["DIP"], df["DIM"])
    df["DMI_Death_Cross"]  = crossunder(df["DIP"], df["DIM"])
    
    dmi_golden_cross_points = df[df["DMI_Golden_Cross"]][["DIP"]]
    dmi_death_cross_points  = df[df["DMI_Death_Cross"]][["DIM"]]

    dmi_golden_cross_points.reset_index(inplace=True)
    dmi_death_cross_points.reset_index(inplace=True)
    
    dmi_gcp_data = dmi_golden_cross_points[['Date', 'DIP']]
    dmi_dcp_data = dmi_death_cross_points [['Date', 'DIM']]
    
    dmi_gcp_data_str = dmi_gcp_data["Date"].astype(str)
    dmi_dcp_data_str = dmi_dcp_data["Date"].astype(str)

    dmi_gc_result_list = []
    dmi_dc_result_list = []
    
    for date_str in dmi_gcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        dmi_gc_result_list.append(timestamp)
    
    for date_str in dmi_dcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        dmi_dc_result_list.append(timestamp)
    
    # ------
    
    # 定義 RSI 上下界
    rsi_over = pd.Series(70, index=df.index)  # 创建与 RSI 列相同长度的 Series，值为 80
    rsi_down = pd.Series(30, index=df.index)
        
    # 檢測 RSI 穿越點
    df["RSI_Above_80"] = crossover(df["RSI"], rsi_over)
    df["RSI_Below_20"] = crossunder(df["RSI"], rsi_down)

    overbuy = df[df["RSI_Above_80"]][["RSI"]]
    oversell  = df[df["RSI_Below_20"]][["RSI"]]

    overbuy.reset_index(inplace=True)
    oversell.reset_index(inplace=True)

    ob_data = overbuy[['Date', 'RSI']]
    os_data = oversell [['Date', 'RSI']]

    ob_data_str = ob_data["Date"].astype(str)
    os_data_str = os_data["Date"].astype(str)

    ob_result_list = []
    os_result_list = []

    for date_str in ob_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        ob_result_list.append(timestamp)

    for date_str in os_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        os_result_list.append(timestamp)
        
    # ------

    # 總資料
    df.reset_index(inplace=True)
    df_data = df[['Date', 'RSI', 'ADX', 'DIP', 'DIM']]
    df_date_str = df_data["Date"].astype(str)

    rsi_result_list = []

    for date_str in df_date_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        rsi_result_list.append(timestamp)
        
    # ------
        
    # 資料後處理
    list_adx              = df_data['ADX'].tolist()
    list_rsi              = df_data['RSI'].tolist()
    list_dip              = df_data['DIP'].tolist()
    list_dim              = df_data['DIM'].tolist()
    list_dmi_gc           = dmi_gcp_data['DIP'].tolist()
    list_dmi_dc           = dmi_dcp_data['DIM'].tolist()
    list_ob               = ob_data['RSI'].tolist()
    list_os               = os_data['RSI'].tolist()

    combined_list_adx     = [[date, adx] for date, adx in zip(rsi_result_list, list_adx)]
    combined_list_rsi     = [[date, rsi] for date, rsi in zip(rsi_result_list, list_rsi)]
    combined_list_dip     = [[date, dip] for date, dip in zip(rsi_result_list, list_dip)]
    combined_list_dim     = [[date, dim] for date, dim in zip(rsi_result_list, list_dim)]
    combined_list_dmi_gc  = [[date, dip] for date, dip in zip(dmi_gc_result_list, list_dmi_gc)]
    combined_list_dmi_dc  = [[date, dim] for date, dim in zip(dmi_dc_result_list, list_dmi_dc)]
    combined_list_ob      = [[date, ob]  for date, ob  in zip(ob_result_list, list_ob)]
    combined_list_os      = [[date, os]  for date, os  in zip(os_result_list, list_os)]

    combined_array_adx    = np.array(combined_list_adx)
    combined_array_rsi    = np.array(combined_list_rsi)
    combined_array_dip    = np.array(combined_list_dip)
    combined_array_dim    = np.array(combined_list_dim)
    combined_array_dmi_gc = np.array(combined_list_dmi_gc)
    combined_array_dmi_dc = np.array(combined_list_dmi_dc)
    combined_array_ob     = np.array(combined_list_ob)
    combined_array_os     = np.array(combined_list_os)

    data_stock_adx        = combined_array_adx.tolist()
    data_stock_rsi        = combined_array_rsi.tolist()
    data_stock_dip        = combined_array_dip.tolist()
    data_stock_dim        = combined_array_dim.tolist()
    data_stock_dmi_gc     = combined_array_dmi_gc.tolist()
    data_stock_dmi_dc     = combined_array_dmi_dc.tolist()
    data_stock_ob         = combined_array_ob.tolist()
    data_stock_os         = combined_array_os.tolist()
    
    # print('-------------------')
    # # print(data_stock_dmi_gc)
    # print('-------------------')
    # # print(data_stock_dmi_dc)
    # print('-------------------')
    
    return data_stock_dmi_dc, data_stock_dmi_gc, data_stock_adx, data_stock_rsi, data_stock_ob, data_stock_os, data_stock_dip, data_stock_dim

# K線
def kline(stock_inductor, start_date_inductor, end_date_inductor):
    stock = pd.DataFrame(yf.download(stock_inductor, start_date_inductor, end_date_inductor))


    # ------------------------------------- 自己寫 --------------------------------------------
    # pattern_matches_evening = []
    # pattern_matches_morning = []
    # pattern_matches_red_3   = []
    # pattern_matches_bla_3   = []

    # # 遍历数据，逐行判断条件
    # for i in range(2, len(stock)):
    #     # 取第1天、第2天和第3天的数据
    #     day1 = stock.iloc[i - 2]
    #     day2 = stock.iloc[i - 1]
    #     day3 = stock.iloc[i]

    #     # 提取每一天的具体数值
    #     day1_close = float(day1['Close'])
    #     day1_open = float(day1['Open'])
    #     day2_open = float(day2['Open'])
    #     day2_close = float(day2['Close'])
    #     day3_open = float(day3['Open'])
    #     day3_close = float(day3['Close'])

        # 计算第1天和第3天的实体长度（收盘价 - 开盘价的绝对值）
        # day1_body_length = abs(day1_close - day1_open)
        # day3_body_length = abs(day3_close - day3_open)

        # 判断条件：
        # 1. 第2天的开盘价和收盘价都要大于第1天的收盘价以及第3天的开盘价
        # 2. 第3天的实体长度大于第1天实体长度的一半
        # if (day1_close > day1_open    and 
        #     day3_open  > day3_close   and 
        #     day2_open  > day1_close   and 
        #     day2_close > day1_close   and 
        #     day2_open  > day3_close   and 
        #     day2_close > day3_close   and 
        #     day2_open  > day3_open    and 
        #     day2_close > day3_open    and 
        #     day3_body_length > (day1_body_length / 2)):
        #     pattern_matches_evening.append([stock.index[i].timestamp()*1000, day3_close])
            
        # if (day3_close > day3_open    and
        #     day1_open  > day1_close   and
        #     day2_open  < day1_close   and 
        #     day2_close < day1_close   and 
        #     day2_open  < day3_close   and 
        #     day2_close < day3_close   and 
        #     day2_open  < day3_open    and 
        #     day2_close < day3_open    and 
        #     day3_body_length > (day1_body_length / 2)):
        #     pattern_matches_morning.append([stock.index[i].timestamp()*1000, day3_close])
        
        
        # 紅黑三兵
        # if (day1_close > day1_open  and
        #     day2_close > day2_open  and
        #     day3_close > day3_open  and
        #     day2_close < day3_open  and 
        #     day2_close < day3_close and
        #     day1_close < day2_open  and
        #     day1_close < day2_close):
        #     pattern_matches_red_3.append([stock.index[i].timestamp()*1000, day3_close])
            
        # if (day1_close < day1_open  and
        #     day2_close < day2_open  and
        #     day3_close < day3_open  and
        #     day2_close < day1_close and
        #     day2_close < day1_open  and 
        #     day3_close < day2_close and  
        #     day3_close < day2_open):
        #     pattern_matches_bla_3.append([stock.index[i].timestamp()*1000, day3_close])
            
    # print("符合黃昏之星的日期：", pattern_matches_evening)
    # print("符合清晨之星的日期：", pattern_matches_morning)
    # print("符合紅三兵的日期是：", pattern_matches_red_3)
    # print("符合黑三兵的日期是：", pattern_matches_bla_3)
    
    # stock = pd.DataFrame(yf.download("TSLA", start='2023-01-01', end='2023-12-31'))

    # ------------------------------------- 自己寫 --------------------------------------------
 
    # ------------------------------------- talib --------------------------------------------
    # 黃昏之星
    stock = stock[['Open', 'High', 'Low', 'Close']].dropna()

    open_prices  = stock['Open'].to_numpy(dtype=np.float64)
    high_prices  = stock['High'].to_numpy(dtype=np.float64)
    low_prices   = stock['Low'].to_numpy(dtype=np.float64)
    close_prices = stock['Close'].to_numpy(dtype=np.float64)

    open_prices  = open_prices.ravel()
    high_prices  = high_prices.ravel()
    low_prices   = low_prices.ravel()
    close_prices = close_prices.ravel()

    # 黃昏之星
    evening_star = talib.CDLEVENINGSTAR(open_prices, high_prices, low_prices, close_prices, penetration=0.3)
    
    # 清晨之星
    morning_star = talib.CDLMORNINGSTAR(open_prices, high_prices, low_prices, close_prices, penetration=0.3)
    
    # 紅三兵
    red_3        = talib.CDL3WHITESOLDIERS(open_prices, high_prices, low_prices, close_prices)
    
    # 黑三兵
    bla_3        = talib.CDL3BLACKCROWS(open_prices, high_prices, low_prices, close_prices)
    
    # 吞噬型態
    engulfing    = talib.CDLENGULFING(open_prices, high_prices, low_prices, close_prices)

    stock['EveningStar'] = evening_star
    stock['MorningStar'] = morning_star
    stock['Red_3'] = red_3
    stock['Bla_3'] = bla_3
    stock['Engulfing'] = engulfing

    # 黃昏之星
    evening_star_dates = stock[stock['EveningStar'] != 0   ][['EveningStar', 'Close']]
    # 清晨之星
    morning_star_dates = stock[stock['MorningStar'] != 0   ][['MorningStar', 'Close']]
    # 紅三兵
    red_3_dates        = stock[stock['Red_3']       != 0   ][['Red_3', 'Close']]
    # 黑三兵
    bla_3_dates        = stock[stock['Bla_3']       != 0   ][['Bla_3', 'Close']]
    # 看漲吞噬
    bullish_engulfing  = stock[stock['Engulfing']   ==  100][['Close']]
    # 看跌吞噬
    bearish_engulfing  = stock[stock['Engulfing']   == -100][['Close']]
    
    # print('----------------123')
    # print(evening_star_dates)
    # print('----------------123')
    
    # print(evening_star_dates)
    # print('morning_star : ', morning_star)
    # print('morning_star_dates : ', morning_star_dates)
    # print('see Here')
    # print('red_3_dates : ', red_3_dates)
    # print('bla_3_dates : ', bla_3_dates)
    # print(bullish_engulfing)
    # print(bearish_engulfing)
        
    pattern_matches_evening = []
    for index, row in evening_star_dates.iterrows():
        timestamp = int(pd.Timestamp(index).timestamp())
        close_price = float(row['Close'])
        pattern_matches_evening.append([timestamp * 1000, close_price])
        
    pattern_matches_morning = []   
    for index, row in morning_star_dates.iterrows():
        timestamp = int(pd.Timestamp(index).timestamp())
        close_price = float(row['Close'])
        pattern_matches_morning.append([timestamp * 1000, close_price])
        
    pattern_matches_red_3   = []
    for index, row in red_3_dates.iterrows():
        timestamp = int(pd.Timestamp(index).timestamp())
        close_price = float(row['Close'])
        pattern_matches_red_3.append([timestamp * 1000, close_price])
    
    pattern_matches_bla_3   = []
    for index, row in bla_3_dates.iterrows():
        timestamp = int(pd.Timestamp(index).timestamp())
        close_price = float(row['Close'])
        pattern_matches_bla_3.append([timestamp * 1000, close_price])
        
    bullish_engulfing_list = []   
    for index, row in bullish_engulfing.iterrows():
        timestamp = int(pd.Timestamp(index).timestamp())
        close_price = float(row['Close'])
        bullish_engulfing_list.append([timestamp * 1000, close_price])
        
    bearish_engulfing_list = []
    for index, row in bearish_engulfing.iterrows():
        timestamp = int(pd.Timestamp(index).timestamp())
        close_price = float(row['Close'])
        bearish_engulfing_list.append([timestamp * 1000, close_price])
        
    pattern_matches_evening = [[item[0] - (8 * 60 * 60 * 1000), item[1]] for item in pattern_matches_evening]
    pattern_matches_morning = [[item[0] - (8 * 60 * 60 * 1000), item[1]] for item in pattern_matches_morning]
    pattern_matches_red_3 = [[item[0] - (8 * 60 * 60 * 1000), item[1]] for item in pattern_matches_red_3]
    pattern_matches_bla_3 = [[item[0] - (8 * 60 * 60 * 1000), item[1]] for item in pattern_matches_bla_3]
    bullish_engulfing_list = [[item[0] - (8 * 60 * 60 * 1000), item[1]] for item in bullish_engulfing_list]
    bearish_engulfing_list = [[item[0] - (8 * 60 * 60 * 1000), item[1]] for item in bearish_engulfing_list]
    
    return pattern_matches_evening, pattern_matches_morning, pattern_matches_red_3, pattern_matches_bla_3, bullish_engulfing_list, bearish_engulfing_list


def trans(data):
    
    converted_data = [
        [datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d'), value]
        for timestamp, value in data
    ]

    return converted_data











# def find_low_volume_days(df):
#     """
#     找出没爆大量的日期，并返回一个新的 DataFrame
#     条件：当日量能 <= 5日均量
#     """
#     low_volume_days = df[df['Volume'] <= df['5DayAvgVolume']][['Volume']]
#     low_volume_days = low_volume_days.reset_index()
#     low_volume_days = low_volume_days.rename(columns={'index': 'Date', 'Volume': 'LowVolume'})
    
#     return low_volume_days




# first page for module course

def inductor_tra(
    stock_inductor, start_date_inductor, end_date_inductor,
    fastk_period, slowk_period, slowd_period, 
    fastperiod, slowperiod, signalperiod,
    bb_timeperiod, nbdevup, nbdevdn, matype,
    rsi_timeperiod, dmi_timeperiod
    ):

    
    df = pd.DataFrame(yf.download(stock_inductor, start=start_date_inductor, end=end_date_inductor))
    
    
    # -----------------------------------  Band   ---------------------------------------------------------------------------------------------------------

    data_stock_Band_mid, data_stock_Band_upper, data_stock_Band_lower, data_stock_band_gc, data_stock_band_dc = band(
                                                                                                                    stock_inductor, start_date_inductor, end_date_inductor,
                                                                                                                    bb_timeperiod, nbdevup, nbdevdn, matype
                                                                                                                    )
 

    
    # -----------------------------------  KD指標  ---------------------------------------------------------------------------------------------------------

    data_stock_K, data_stock_D, data_stock_K_gc, data_stock_D_dc = kd(
                                                                    stock_inductor, start_date_inductor, end_date_inductor,
                                                                    fastk_period, slowk_period, slowd_period,
                                                                    )
    

    # ----------------------------------- MACD指標 ---------------------------------------------------------------------------------------------------------

    data_stock_MACD_fast, data_stock_MACD_slow, data_stock_MACD_hist, data_stock_MACD_fast_gc, data_stock_MACD_slow_dc = macd(
                                                                                                                            stock_inductor, start_date_inductor, end_date_inductor,
                                                                                                                            fastperiod, slowperiod, signalperiod
                                                                                                                            )


    # ---------------------------------- RSI & ADX ---------------------------------------------------------------------------------------------------------
    # 參考下面rsi函式
    data_stock_dmi_gc, data_stock_dmi_dc, data_stock_adx, data_stock_rsi, data_stock_ob, data_stock_os, data_stock_dip , data_stock_dim = rsi(stock_inductor, start_date_inductor, end_date_inductor, rsi_timeperiod, dmi_timeperiod)
    
    
    # ----------------------------------   Kline   ---------------------------------------------------------------------------------------------------------

    pattern_matches_evening, pattern_matches_morning, pattern_matches_red_3, pattern_matches_bla_3 ,bullish_engulfing_list, bearish_engulfing_list = kline(stock_inductor, start_date_inductor, end_date_inductor)
    
    

    
    
    # ----------------------------------- 資料後處理 ---------------------------------------------------------------------------------------------------------
    
    df.reset_index(inplace=True)
    # df_data = df[['Date', 'K', 'D', 'RSV', 'MACD_fast', 'MACD_slow', 'MACD_Histogram', 'Mid_Band', 'Upper_Band', 'Lower_Band', 'Open', 'High', 'Low', 'Adj Close']]
    df_data = df[['Date', 'Open', 'High', 'Low', 'Adj Close']]
    df_date_str = df_data["Date"].astype(str)
    result_list = []
    
    for date_str in df_date_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        result_list.append(timestamp)
    
    # 蠟燭圖
    list_open                   = df_data['Open'].tolist()
    list_high                   = df_data['High'].tolist()
    list_low                    = df_data['Low'].tolist()
    list_adj_close              = df_data['Adj Close'].tolist()

    combined_list_candle        = [[date, open, high, low, adjclose] for date, open, high, low, adjclose in zip(result_list, list_open, list_high, list_low, list_adj_close)]
    
    combined_array_candle       = np.array(combined_list_candle) 

    data_stock_candle           = combined_array_candle.tolist()

    
    tf_data = {
        "data_stock_K_gc": data_stock_K_gc,
        "data_stock_D_dc": data_stock_D_dc,
        "data_stock_MACD_fast_gc": data_stock_MACD_fast_gc,
        "data_stock_MACD_slow_dc": data_stock_MACD_slow_dc,
        "data_stock_band_gc": data_stock_band_gc,
        "data_stock_band_dc": data_stock_band_dc,
        "data_stock_ob": data_stock_ob,
        "data_stock_os": data_stock_os,
        'data_stock_dmi_gc' : data_stock_dmi_gc,
        'data_stock_dmi_dc' : data_stock_dmi_dc,
        'pattern_matches_morning' : pattern_matches_morning,
        'pattern_matches_evening' : pattern_matches_evening,
        'pattern_matches_red_3'   : pattern_matches_red_3,
        'pattern_matches_bla_3'   : pattern_matches_bla_3,
        'bullish_engulfing_list'  : bullish_engulfing_list,
        'bearish_engulfing_list'  : bearish_engulfing_list
    }
    
    entry_df, exit_df = organize_signals_to_titles(tf_data)
    
    # print("Entry Signals:")
    # print(entry_df)
    # print("\nExit Signals:")
    # print(exit_df)
    
    #  DataFrame to JSON 
    entry_signals_json = entry_df.reset_index().rename(columns={"index": "date"}).to_dict(orient="records")
    exit_signals_json = exit_df.reset_index().rename(columns={"index": "date"}).to_dict(orient="records")

    # final_JSON 
    final_json = {
        "entry_signals": entry_signals_json,
        "exit_signals": exit_signals_json
    }
    
    # print('final_json : ', final_json)
    # print('pattern_matches_morning : ', pattern_matches_morning)
    # print('pattern_matches_red_3 : ', pattern_matches_red_3)
    # print('bullish_engulfing_list : ', bullish_engulfing_list)
    
    response = {
        'stock_inductor'          : stock_inductor,
        'data_stock_K'            : data_stock_K,
        'data_stock_D'            : data_stock_D,
        'data_stock_K_gc'         : data_stock_K_gc,
        'data_stock_D_dc'         : data_stock_D_dc,
        'data_stock_MACD_fast'    : data_stock_MACD_fast,
        'data_stock_MACD_slow'    : data_stock_MACD_slow,
        'data_stock_MACD_fast_gc' : data_stock_MACD_fast_gc,
        'data_stock_MACD_slow_dc' : data_stock_MACD_slow_dc,
        'data_stock_MACD_hist'    : data_stock_MACD_hist,
        'data_stock_Band_mid'     : data_stock_Band_mid,
        'data_stock_Band_upper'   : data_stock_Band_upper,
        'data_stock_Band_lower'   : data_stock_Band_lower,
        'data_stock_band_gc'      : data_stock_band_gc,
        'data_stock_band_dc'      : data_stock_band_dc,
        'data_stock_candle'       : data_stock_candle,
        'data_stock_adx'          : data_stock_adx,
        'data_stock_rsi'          : data_stock_rsi,
        'data_stock_ob'           : data_stock_ob,
        'data_stock_os'           : data_stock_os,
        'data_stock_dip'          : data_stock_dip,
        'data_stock_dim'          : data_stock_dim,
        'data_stock_dmi_gc'       : data_stock_dmi_gc,
        'data_stock_dmi_dc'       : data_stock_dmi_dc,
        'pattern_matches_evening' : pattern_matches_evening,
        'pattern_matches_morning' : pattern_matches_morning,
        'pattern_matches_red_3'   : pattern_matches_red_3,
        'pattern_matches_bla_3'   : pattern_matches_bla_3,
        'bullish_engulfing_list'  : bullish_engulfing_list,
        'bearish_engulfing_list'  : bearish_engulfing_list,
        'final_json'              : final_json
    }

    return response

# 布林帶 
def band(
    stock_inductor, start_date_inductor, end_date_inductor,
    bb_timeperiod, nbdevup, nbdevdn, matype,
    ):
    
    print('----- in band method -----')
    print(stock_inductor)
    print(start_date_inductor)
    print(end_date_inductor)
    print('bb_timeperiod', bb_timeperiod)
    print('nbdevup', nbdevup)
    print('nbdevdn', nbdevdn)
    print('matype', matype)
    
    data = pd.DataFrame(yf.download(stock_inductor, start_date_inductor, end_date_inductor))

    # 处理列名（如果是多层列名，则获取第一个层级）
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    # 计算布林通道
    upper_band, middle_band, lower_band = talib.BBANDS(data['Close'], timeperiod=bb_timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=matype)

    # 将布林通道的结果加入到 DataFrame
    data['UpperBand'] = upper_band
    data['MiddleBand'] = middle_band
    data['LowerBand'] = lower_band

    # 判断是否突破上轨或跌破下轨
    data['BreakUpperBand'] = data['Close'] > data['UpperBand']  # 收盘价 > 上轨
    data['BreakLowerBand'] = data['Close'] < data['LowerBand']  # 收盘价 < 下轨

    # 提取突破上轨和跌破下轨的点
    break_upper_points = data[data['BreakUpperBand']][["Close"]]
    break_lower_points = data[data['BreakLowerBand']][["Close"]]

    break_upper_points.reset_index(inplace=True)
    break_lower_points.reset_index(inplace=True)

    band_gcp_data = break_upper_points[['Date', 'Close']]
    band_dcp_data = break_lower_points [['Date', 'Close']]

    band_gcp_data_str = band_gcp_data["Date"].astype(str)
    band_dcp_data_str = band_dcp_data["Date"].astype(str)

    band_gc_result_list = []
    band_dc_result_list = []

    for date_str in band_gcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        band_gc_result_list.append(timestamp)

    for date_str in band_dcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        band_dc_result_list.append(timestamp)

    data.reset_index(inplace=True)
    band_data = data[['Date', 'MiddleBand', 'UpperBand', 'LowerBand']]
    data_date_str = band_data["Date"].astype(str)
    band_result_list = []

    for date_str in data_date_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        band_result_list.append(timestamp)

    list_Band_mid   = band_data['MiddleBand'].tolist()
    list_Band_upper = band_data['UpperBand'].tolist()
    list_Band_lower = band_data['LowerBand'].tolist()
    list_band_gc    = break_upper_points['Close'].tolist()
    list_band_dc    = break_lower_points ['Close'].tolist()

    combined_list_Band_mid      = [[date, band_mid]   for date, band_mid   in zip(band_result_list, list_Band_mid)]
    combined_list_Band_upper    = [[date, band_upper] for date, band_upper in zip(band_result_list, list_Band_upper)]
    combined_list_Band_lower    = [[date, band_lower] for date, band_lower in zip(band_result_list, list_Band_lower)]
    combined_list_band_gc       = [[date, k] for date, k in zip(band_gc_result_list, list_band_gc)]
    combined_list_band_dc       = [[date, d] for date, d in zip(band_dc_result_list, list_band_dc)]

    combined_array_Band_mid     = np.array(combined_list_Band_mid)
    combined_array_Band_upper   = np.array(combined_list_Band_upper)
    combined_array_Band_lower   = np.array(combined_list_Band_lower)
    combined_array_band_gc      = np.array(combined_list_band_gc)
    combined_array_band_dc      = np.array(combined_list_band_dc)

    data_stock_Band_mid         = combined_array_Band_mid.tolist()
    data_stock_Band_upper       = combined_array_Band_upper.tolist()
    data_stock_Band_lower       = combined_array_Band_lower.tolist()
    data_stock_band_gc          = combined_array_band_gc.tolist()
    data_stock_band_dc          = combined_array_band_dc.tolist()

    data_stock_Band_mid   = [item for item in data_stock_Band_mid if not math.isnan(item[1])]
    data_stock_Band_upper = [item for item in data_stock_Band_upper if not math.isnan(item[1])]
    data_stock_Band_lower = [item for item in data_stock_Band_lower if not math.isnan(item[1])]
    
    print('----- end band methon -----')

    return data_stock_Band_mid, data_stock_Band_upper, data_stock_Band_lower, data_stock_band_gc, data_stock_band_dc

# MACD指標
def macd(
    stock_inductor, start_date_inductor, end_date_inductor,
    fastperiod, slowperiod, signalperiod
    ):
    
    print('----- in macd method -----')
    print(stock_inductor)
    print(start_date_inductor)
    print(end_date_inductor)    
    print('fastperiod', fastperiod)
    print('slowperiod', slowperiod)
    print('signalperiod', signalperiod)

    data = pd.DataFrame(yf.download(stock_inductor, start_date_inductor, end_date_inductor))
    # data = yf.download('AAPL', start='2024-06-01', end='2024-12-31')

    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    close = data['Close']

    # 计算 MACD 指标
    macd, signal, hist = talib.MACD(close, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)

    # 将 MACD, Signal, Histogram 加入到 DataFrame
    data['MACD'] = macd
    data['Signal'] = signal
    data['Histogram'] = hist

    # 定义金叉和死叉函数
    def crossover(series1, series2):
        return (series1 > series2) & (series1.shift(1) <= series2.shift(1))

    def crossunder(series1, series2):
        return (series1 < series2) & (series1.shift(1) >= series2.shift(1))

    # 找出金叉和死叉
    data["MACD_Golden_Cross"] = crossover(data["MACD"], data["Signal"])
    data["MACD_Death_Cross"] = crossunder(data["MACD"], data["Signal"])

    # 提取金叉和死叉点
    macd_golden_cross_points = data[data["MACD_Golden_Cross"]][["Close", "MACD"]]
    macd_death_cross_points = data[data["MACD_Death_Cross"]][["Close", "MACD"]]

    macd_golden_cross_points.reset_index(inplace=True)
    macd_death_cross_points.reset_index(inplace=True)

    macd_gcp_data = macd_golden_cross_points[['Date', 'MACD']]
    macd_dcp_data = macd_death_cross_points [['Date', 'MACD']]

    macd_gcp_data_str = macd_gcp_data["Date"].astype(str)
    macd_dcp_data_str = macd_dcp_data["Date"].astype(str)

    macd_gc_result_list = []
    macd_dc_result_list = []

    for date_str in macd_gcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        macd_gc_result_list.append(timestamp)

    for date_str in macd_dcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        macd_dc_result_list.append(timestamp)


    data.reset_index(inplace=True)
    macd_data = data[['Date', 'MACD', 'Signal', 'Histogram']]
    data_date_str = macd_data["Date"].astype(str)
    macd_result_list = []

    for date_str in data_date_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        macd_result_list.append(timestamp)

    list_MACD_fast              = macd_data['MACD'].tolist()
    list_MACD_slow              = macd_data['Signal'].tolist()
    list_MACD_hist              = macd_data['Histogram'].tolist()
    list_MACD_fast_gc           = macd_golden_cross_points['MACD'].tolist()
    list_MACD_slow_dc           = macd_death_cross_points['MACD'].tolist()


    combined_list_MACD_fast     = [[date, macd_fast]  for date, macd_fast  in zip(macd_result_list, list_MACD_fast)]
    combined_list_MACD_slow     = [[date, macd_slow]  for date, macd_slow  in zip(macd_result_list, list_MACD_slow)]
    combined_list_MACD_hist     = [[date, macd_hist]  for date, macd_hist  in zip(macd_result_list, list_MACD_hist)]
    combined_list_MACD_fast_gc  = [[date, macd_fast]  for date, macd_fast  in zip(macd_gc_result_list, list_MACD_fast_gc)]
    combined_list_MACD_slow_dc  = [[date, macd_fast]  for date, macd_fast  in zip(macd_dc_result_list, list_MACD_slow_dc)]

    combined_array_MACD_fast    = np.array(combined_list_MACD_fast)
    combined_array_MACD_slow    = np.array(combined_list_MACD_slow)
    combined_array_MACD_hist    = np.array(combined_list_MACD_hist)
    combined_array_MACD_fast_gc = np.array(combined_list_MACD_fast_gc)
    combined_array_MACD_slow_dc = np.array(combined_list_MACD_slow_dc)

    data_stock_MACD_fast        = combined_array_MACD_fast.tolist()
    data_stock_MACD_slow        = combined_array_MACD_slow.tolist()
    data_stock_MACD_hist        = combined_array_MACD_hist.tolist()
    data_stock_MACD_fast_gc     = combined_array_MACD_fast_gc.tolist()
    data_stock_MACD_slow_dc     = combined_array_MACD_slow_dc.tolist()
    
    data_stock_MACD_fast = [item for item in data_stock_MACD_fast if not math.isnan(item[1])]
    data_stock_MACD_slow = [item for item in data_stock_MACD_slow if not math.isnan(item[1])]
    data_stock_MACD_hist = [item for item in data_stock_MACD_hist if not math.isnan(item[1])]
    
    print('----- end macd method -----')
    
    return data_stock_MACD_fast, data_stock_MACD_slow, data_stock_MACD_hist, data_stock_MACD_fast_gc, data_stock_MACD_slow_dc

# KD指標
def kd(
    stock_inductor, start_date_inductor, end_date_inductor,
    fastk_period, slowk_period, slowd_period,
    ):
    
    print('----- in kd method -----')
    print(stock_inductor)
    print(start_date_inductor)
    print(end_date_inductor)
    print('fastk_period', fastk_period)
    print('slowk_period', slowk_period)
    print('slowd_period', slowd_period)
    
    data=pd.DataFrame(yf.download(stock_inductor, start_date_inductor, end_date_inductor))

    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    # Step 2: 計算 K 線和 D 線（隨機指標）
    # 使用 talib.STOCH 計算 K 線和 D 線
    # 將 pandas DataFrame 轉換為 numpy.ndarray
    high = data['High'].values
    low = data['Low'].values
    close = data['Close'].values

    # 計算 KD 指標
    fastk, fastd = talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)

    # 將計算的 K 線和 D 線加入到數據框中
    data['K'] = fastk
    data['D'] = fastd

    # 定義金叉和死叉函数
    def crossover(series1, series2):
        return (series1 > series2) & (series1.shift(1) <= series2.shift(1))

    def crossunder(series1, series2):
        return (series1 < series2) & (series1.shift(1) >= series2.shift(1))

    # 找出金叉和死叉
    data['KD_Golden_Cross'] = crossover(data['K'], data['D'])
    data['KD_Death_Cross'] = crossunder(data['K'], data['D'])

    # 取金叉和死叉点
    kd_golden_cross_points = data[data['KD_Golden_Cross']][['K']]
    kd_death_cross_points  = data[data['KD_Death_Cross']][['D']]

    kd_golden_cross_points.reset_index(inplace=True)
    kd_death_cross_points.reset_index(inplace=True)

    kd_gcp_data = kd_golden_cross_points[['Date', 'K']]
    kd_dcp_data = kd_death_cross_points [['Date', 'D']]

    kd_gcp_data_str = kd_gcp_data["Date"].astype(str)
    kd_dcp_data_str = kd_dcp_data["Date"].astype(str)

    kd_gc_result_list = []
    kd_dc_result_list = []

    for date_str in kd_gcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        kd_gc_result_list.append(timestamp)

    for date_str in kd_dcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        kd_dc_result_list.append(timestamp)

    data.reset_index(inplace=True)
    kd_data = data[['Date', 'K', 'D']]
    data_date_str = kd_data["Date"].astype(str)
    kd_result_list = []

    for date_str in data_date_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        kd_result_list.append(timestamp)
        
    list_K                      = kd_data['K'].tolist()
    list_D                      = kd_data['D'].tolist()
    list_K_gc                   = kd_golden_cross_points['K'].tolist()
    list_D_dc                   = kd_death_cross_points ['D'].tolist()

    combined_list_K             = [[date, k]          for date, k          in zip(kd_result_list, list_K)]
    combined_list_D             = [[date, d]          for date, d          in zip(kd_result_list, list_D)]
    combined_list_K_gc          = [[date, k]          for date, k          in zip(kd_gc_result_list, list_K_gc)]
    combined_list_D_dc          = [[date, d]          for date, d          in zip(kd_dc_result_list, list_D_dc)]

    combined_array_K            = np.array(combined_list_K)
    combined_array_D            = np.array(combined_list_D)
    combined_array_K_gc         = np.array(combined_list_K_gc)
    combined_array_D_dc         = np.array(combined_list_D_dc)

    data_stock_K                = combined_array_K.tolist()
    data_stock_D                = combined_array_D.tolist()
    data_stock_K_gc             = combined_array_K_gc.tolist()
    data_stock_D_dc             = combined_array_D_dc.tolist()

    data_stock_K = [item for item in data_stock_K if not math.isnan(item[1])]
    data_stock_D = [item for item in data_stock_D if not math.isnan(item[1])]
    
    print('----- end kd method -----')
    
    return data_stock_K, data_stock_D, data_stock_K_gc, data_stock_D_dc

# RSI指標
def rsi(stock_inductor, start_date_inductor, end_date_inductor, rsi_timeperiod, dmi_timeperiod):
    
    print('in rsi method')
    print(stock_inductor)
    print(start_date_inductor)
    print(end_date_inductor)
    print('rsi_timeperiod', rsi_timeperiod)
    
    df=pd.DataFrame(yf.download(stock_inductor, start_date_inductor, end_date_inductor))
    
    # 将所有列名转换为小写
    df.columns = [col.lower() for col in df.columns]
    
    # 計算 RSI、ADX 
    df["ADX"] = abstract.ADX(df, timeperiod = dmi_timeperiod)
    df["RSI"] = abstract.RSI(df, timeperiod = rsi_timeperiod)

    # ------
    
    # 計算DMI
    high = df['high']
    low = df['low']
    close = df['close']
    # 計算 +DI, -DI 和 ADX
    df["DIP"] = talib.PLUS_DI(high, low, close, timeperiod=dmi_timeperiod)
    df["DIM"] = talib.MINUS_DI(high, low, close, timeperiod=dmi_timeperiod)
    
    # ------


    # 删除包含 NaN 的行
    df.dropna(subset=["RSI"], inplace=True)
    df.dropna(subset=["ADX"], inplace=True)
    df.dropna(subset=["DIP"], inplace=True)
    df.dropna(subset=["DIM"], inplace=True)

    # DMI金叉死叉
    df["DMI_Golden_Cross"] = crossover(df["DIP"], df["DIM"])
    df["DMI_Death_Cross"]  = crossunder(df["DIP"], df["DIM"])
    
    dmi_golden_cross_points = df[df["DMI_Golden_Cross"]][["DIP"]]
    dmi_death_cross_points  = df[df["DMI_Death_Cross"]][["DIM"]]

    dmi_golden_cross_points.reset_index(inplace=True)
    dmi_death_cross_points.reset_index(inplace=True)
    
    dmi_gcp_data = dmi_golden_cross_points[['Date', 'DIP']]
    dmi_dcp_data = dmi_death_cross_points [['Date', 'DIM']]
    
    dmi_gcp_data_str = dmi_gcp_data["Date"].astype(str)
    dmi_dcp_data_str = dmi_dcp_data["Date"].astype(str)

    dmi_gc_result_list = []
    dmi_dc_result_list = []
    
    for date_str in dmi_gcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        dmi_gc_result_list.append(timestamp)
    
    for date_str in dmi_dcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        dmi_dc_result_list.append(timestamp)
    
    # ------
    
    # 定義 RSI 上下界
    rsi_over = pd.Series(70, index=df.index)  # 创建与 RSI 列相同长度的 Series，值为 80
    rsi_down = pd.Series(30, index=df.index)
        
    # 檢測 RSI 穿越點
    df["RSI_Above_80"] = crossover(df["RSI"], rsi_over)
    df["RSI_Below_20"] = crossunder(df["RSI"], rsi_down)

    overbuy = df[df["RSI_Above_80"]][["RSI"]]
    oversell  = df[df["RSI_Below_20"]][["RSI"]]

    overbuy.reset_index(inplace=True)
    oversell.reset_index(inplace=True)

    ob_data = overbuy[['Date', 'RSI']]
    os_data = oversell [['Date', 'RSI']]

    ob_data_str = ob_data["Date"].astype(str)
    os_data_str = os_data["Date"].astype(str)

    ob_result_list = []
    os_result_list = []

    for date_str in ob_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        ob_result_list.append(timestamp)

    for date_str in os_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        os_result_list.append(timestamp)
        
    # ------

    # 總資料
    df.reset_index(inplace=True)
    df_data = df[['Date', 'RSI', 'ADX', 'DIP', 'DIM']]
    df_date_str = df_data["Date"].astype(str)

    rsi_result_list = []

    for date_str in df_date_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        rsi_result_list.append(timestamp)
        
    # ------
        
    # 資料後處理
    list_adx              = df_data['ADX'].tolist()
    list_rsi              = df_data['RSI'].tolist()
    list_dip              = df_data['DIP'].tolist()
    list_dim              = df_data['DIM'].tolist()
    list_dmi_gc           = dmi_gcp_data['DIP'].tolist()
    list_dmi_dc           = dmi_dcp_data['DIM'].tolist()
    list_ob               = ob_data['RSI'].tolist()
    list_os               = os_data['RSI'].tolist()

    combined_list_adx     = [[date, adx] for date, adx in zip(rsi_result_list, list_adx)]
    combined_list_rsi     = [[date, rsi] for date, rsi in zip(rsi_result_list, list_rsi)]
    combined_list_dip     = [[date, dip] for date, dip in zip(rsi_result_list, list_dip)]
    combined_list_dim     = [[date, dim] for date, dim in zip(rsi_result_list, list_dim)]
    combined_list_dmi_gc  = [[date, dip] for date, dip in zip(dmi_gc_result_list, list_dmi_gc)]
    combined_list_dmi_dc  = [[date, dim] for date, dim in zip(dmi_dc_result_list, list_dmi_dc)]
    combined_list_ob      = [[date, ob]  for date, ob  in zip(ob_result_list, list_ob)]
    combined_list_os      = [[date, os]  for date, os  in zip(os_result_list, list_os)]

    combined_array_adx    = np.array(combined_list_adx)
    combined_array_rsi    = np.array(combined_list_rsi)
    combined_array_dip    = np.array(combined_list_dip)
    combined_array_dim    = np.array(combined_list_dim)
    combined_array_dmi_gc = np.array(combined_list_dmi_gc)
    combined_array_dmi_dc = np.array(combined_list_dmi_dc)
    combined_array_ob     = np.array(combined_list_ob)
    combined_array_os     = np.array(combined_list_os)

    data_stock_adx        = combined_array_adx.tolist()
    data_stock_rsi        = combined_array_rsi.tolist()
    data_stock_dip        = combined_array_dip.tolist()
    data_stock_dim        = combined_array_dim.tolist()
    data_stock_dmi_gc     = combined_array_dmi_gc.tolist()
    data_stock_dmi_dc     = combined_array_dmi_dc.tolist()
    data_stock_ob         = combined_array_ob.tolist()
    data_stock_os         = combined_array_os.tolist()
    
    print('----- end rsi method -----')
    
    return data_stock_dmi_dc, data_stock_dmi_gc, data_stock_adx, data_stock_rsi, data_stock_ob, data_stock_os, data_stock_dip, data_stock_dim

# 轉成json至前端顯示datatable
def organize_signals_to_titles(data):
    
    # 初始化标题
    # titles = ["MACD", "BAND", "RSI", "KD", "DMI"]
    titles = ["MACD", "BAND", "RSI", "KD", "DMI", "MORNING", "EVENING", "RED", "BLACK", "BULLISH", "BEARISH"]
    
    # 初始化dict
    entry_dict = {title: {} for title in titles}
    exit_dict = {title: {} for title in titles}

    def classify_and_populate(signal_data, title, is_entry):
        for timestamp, value in signal_data:
            # 時間戳 -> str(日期)
            date = pd.to_datetime(timestamp, unit='ms').strftime('%Y-%m-%d')
            # 根據進出場選擇對應的dict
            target = entry_dict if is_entry else exit_dict
            if date not in target[title]:
                target[title][date] = f"{'Entry' if is_entry else 'Exit'}: {value:.2f}"

    # 數據分類
    classify_and_populate(data.get("data_stock_MACD_fast_gc", []), "MACD", is_entry=True)
    classify_and_populate(data.get("data_stock_MACD_slow_dc", []), "MACD", is_entry=False)
    classify_and_populate(data.get("data_stock_band_gc", []), "BAND", is_entry=False)
    classify_and_populate(data.get("data_stock_band_dc", []), "BAND", is_entry=True)
    classify_and_populate(data.get("data_stock_os", []), "RSI", is_entry=True)
    classify_and_populate(data.get("data_stock_ob", []), "RSI", is_entry=False)
    classify_and_populate(data.get("data_stock_K_gc", []), "KD", is_entry=True)
    classify_and_populate(data.get("data_stock_D_dc", []), "KD", is_entry=False)
    classify_and_populate(data.get("data_stock_dmi_gc", []), "DMI", is_entry=False)
    classify_and_populate(data.get("data_stock_dmi_dc", []), "DMI", is_entry=True)
    classify_and_populate(data.get("pattern_matches_morning", []), "MORNING", is_entry=True)
    classify_and_populate(data.get("pattern_matches_evening", []), "EVENING", is_entry=False)
    classify_and_populate(data.get("pattern_matches_red_3", []), "RED", is_entry=True)
    classify_and_populate(data.get("pattern_matches_bla_3", []), "BLACK", is_entry=False)
    classify_and_populate(data.get("bullish_engulfing_list", []), "BULLISH", is_entry=True)
    classify_and_populate(data.get("bearish_engulfing_list", []), "BEARISH", is_entry=False)
    
    # 獲取所有日期并排序
    all_dates = set()
    for title in titles:
        all_dates.update(entry_dict[title].keys())
        all_dates.update(exit_dict[title].keys())
    all_dates = sorted(all_dates)

    # 建DataFrame
    entry_df = pd.DataFrame(index=all_dates, columns=titles).fillna("-")
    exit_df = pd.DataFrame(index=all_dates, columns=titles).fillna("-")

    for title in titles:
        for date in all_dates:
            if date in entry_dict[title]:
                entry_df.loc[date, title] = entry_dict[title][date]
            if date in exit_dict[title]:
                exit_df.loc[date, title] = exit_dict[title][date]
                
    # 删除所有列值均为 "-" 的行
    entry_df = entry_df[~(entry_df.eq("-").all(axis=1))]
    exit_df = exit_df[~(exit_df.eq("-").all(axis=1))]

    return entry_df, exit_df


