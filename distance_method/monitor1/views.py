from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .common1.user_setting_operation import  UserTrackingHandler, ConnectUserDB
from .common1.func_client import FuncClient
from .daily_update import handle_email
import pandas as pd
import numpy as np
import time
import talib
from talib import abstract
import json
import math
import os
from pathlib import Path
import datetime
import yfinance as yf

# from common import highchart_format 
# from common.postprocessing import handle_api_signals_data, handle_api_bollinger_band_data, handle_api_profit_loss_data, handle_api_exe_signals_data

uth = UserTrackingHandler()
fc = FuncClient()


def web(request):
   
    return (render(request, "monitor1.html"))

@csrf_exempt
def get_track_list(request):
    user = str(request.user)
    tracks = uth.get_all_track_params_combination_from_user(user)
    track_data  = []
    for track in tracks:    
        print('track[4] : ', track[4])
        ele = {
            'track_date': track[0].strftime('%Y-%m-%d'),  # created_at
            'start_date': track[1].strftime('%Y-%m-%d'),  # start_date
            'end_date': track[2].strftime('%Y-%m-%d'),    # end_date 
            'stock1': track[3],                          # stock1
            'fastk_period': track[4],                    # fastk_period
            'slowk_period': track[5],                    # slowk_period
            'slowd_period': track[6],                    # slowd_period
            'fastperiod': track[7],                      # fastperiod
            'slowperiod': track[8],                      # slowperiod
            'signalperiod': track[9],                   # signalperiod
            'bb_timeperiod': track[10],                  # bb_timeperiod
            'nbdevup': track[11],                        # nbdevup
            'nbdevdn': track[12],                        # nbdevdn
            'matype': track[13],                         # matype
            'rsi_timeperiod': track[14],                 # rsi_timeperiod
            'dmi_timeperiod': track[15]                  # dmi_timeperiod
        }
        track_data.append(ele)
        
    if track_data is None:
        """error handling"""
        
    print('track_data : ', track_data)
    
    return JsonResponse({"track_data": track_data}) 

# step1
@csrf_exempt
def add_track(request):

    stock1 = request.POST.get("stock1")
    # stock2 = request.POST.get("stock2")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    
    fastk_period = request.POST.get("fastk_period")
    slowk_period = request.POST.get("slowk_period")
    slowd_period = request.POST.get("slowd_period")
    fastperiod = request.POST.get("fastperiod")
    slowperiod = request.POST.get("slowperiod")
    signalperiod = request.POST.get("signalperiod")
    bb_timeperiod = request.POST.get("bb_timeperiod")
    nbdevup = request.POST.get("nbdevup")
    nbdevdn = request.POST.get("nbdevdn")
    matype = request.POST.get("matype")
    rsi_timeperiod = request.POST.get("rsi_timeperiod")
    dmi_timeperiod = request.POST.get("dmi_timeperiod")
    
    # print('stock1', stock1)
    
    # method = request.POST.get("method")
    # window_sizes = request.POST.get("window_sizes")
    # std = int(request.POST.get("std"))
    
    # step2
    uth.add(
        username=str(request.user),
        start_date=start_date,       
        end_date = end_date,  
        stock1=stock1,        
        fastk_period=fastk_period,
        slowk_period=slowk_period,
        slowd_period=slowd_period,
        fastperiod=fastperiod,
        slowperiod=slowperiod,
        signalperiod=signalperiod,
        bb_timeperiod=bb_timeperiod,
        nbdevup=nbdevup,
        nbdevdn=nbdevdn,
        matype=matype,
        rsi_timeperiod=rsi_timeperiod,
        dmi_timeperiod=dmi_timeperiod,
    )
    
    return JsonResponse({"msg": "Successful!"})

# step3
@csrf_exempt
def remove_track(request):
    # method = request.POST.get('method')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    stock1 = request.POST.get('stock1')
    
    fastk_period = request.POST.get("fastk_period")
    slowk_period = request.POST.get("slowk_period")
    slowd_period = request.POST.get("slowd_period")
    fastperiod = request.POST.get("fastperiod")
    slowperiod = request.POST.get("slowperiod")
    signalperiod = request.POST.get("signalperiod")
    bb_timeperiod = request.POST.get("bb_timeperiod")
    nbdevup = request.POST.get("nbdevup")
    nbdevdn = request.POST.get("nbdevdn")
    matype = request.POST.get("matype")
    rsi_timeperiod = request.POST.get("rsi_timeperiod")
    dmi_timeperiod = request.POST.get("dmi_timeperiod")
    # stock2 = request.POST.get('stock2')
    # window_size = request.POST.get('window_size')
    user = str(request.user)
    # std = request.POST.get('n_times')
    
    # user_tracking_handler = UserTrackingHandler()
    user_email = uth.get_user_email(user)
    
    # 找remove的tracker把他刪掉 --------------------
    
    
    tracker_folder_path = Path.cwd() / "common1" / "tracker_results"
    # file_path = f"{tracker_folder_path}/{user}/{stock1}_{stock2}_{start_date}_{window_size}_{std}.json"
    
    today = datetime.date.today()
    
    method = 'tracker'
    window_size = 200
    std = 2
    
    file_name = f"{user}_{stock1}_{user_email}_{start_date}_{today}_{method}_{window_size}_{std}.json"
    # file_path = f"{tracker_folder_path}/{user}/{user}_{stock1}_{start_date}_{window_size}_{std}.json"
    file_path = f"{tracker_folder_path}/{user}/{user}_{stock1}_{user_email}_{start_date}_{today}_{method}_{window_size}_{std}.json"
    
    
        
    if os.path.exists(file_path):
        # with open(file_path, 'r') as file:
        #     data = json.load(file) 
        try:
            os.remove(file_path)
            print(f"File {file_name} removed successfully.")
        except Exception as e:
            print(f"Failed to remove file {file_name}: {str(e)}")
    else:
        # data = inductor_tra(stock1, start_date, end_date)
        print(f"File {file_name} does not exist.")
    # andrew_AMD_2021-01-01_200_2.json 
        
    # -------------------------------------------
    
    # step4
    uth.remove(
        username=user,
        start_date=start_date,       
        end_date = end_date,  
        stock1=stock1,
        fastk_period=fastk_period,
        slowk_period=slowk_period,
        slowd_period=slowd_period,
        fastperiod=fastperiod,
        slowperiod=slowperiod,
        signalperiod=signalperiod,
        bb_timeperiod=bb_timeperiod,
        nbdevup=nbdevup,
        nbdevdn=nbdevdn,
        matype=matype,
        rsi_timeperiod=rsi_timeperiod,  
        dmi_timeperiod=dmi_timeperiod,           
    )
        
    return JsonResponse({'msg': 'Successful'})

@csrf_exempt
def run_tracker(request):
    start_date = request.POST.get('start_date')
    end_date = datetime.date.today().strftime('%Y-%m-%d')
    stock1 = request.POST.get('stock1')
    fastk_period = request.POST.get('fastk_period')
    slowk_period = request.POST.get('slowk_period')
    slowd_period = request.POST.get('slowd_period')
    fastperiod = request.POST.get('fastperiod')
    slowperiod = request.POST.get('slowperiod')
    signalperiod = request.POST.get('signalperiod')
    bb_timeperiod = request.POST.get('bb_timeperiod')
    nbdevup = request.POST.get('nbdevup')
    nbdevdn = request.POST.get('nbdevdn')
    matype = request.POST.get('matype')
    rsi_timeperiod = request.POST.get('rsi_timeperiod')
    dmi_timeperiod = request.POST.get('dmi_timeperiod')
    user = str(request.user)

    # user_tracking_handler = UserTrackingHandler()
    user_email = uth.get_user_email(user)
    
    print(stock1)
    print(start_date)
    print(end_date)
    print(user)
    print(user_email)
    print(f"fastk_period: {fastk_period}")
    print(f"slowk_period: {slowk_period}")
    print(f"slowd_period: {slowd_period}")
    print(f"fastperiod: {fastperiod}")
    print(f"slowperiod: {slowperiod}")
    print(f"signalperiod: {signalperiod}")
    print(f"bb_timeperiod: {bb_timeperiod}")
    print(f"nbdevup: {nbdevup}")
    print(f"nbdevdn: {nbdevdn}")
    print(f"matype: {matype}")
    print(f"rsi_timeperiod: {rsi_timeperiod}")
    print(f"dmi_timeperiod: {dmi_timeperiod}")
    # andrew_ASML_jennybaby4wi@gmail.com_2021-01-01_2024-01-01_tracker_200_2
    # andrew_ASML_jennybaby4wi@gmail.com_2021-01-01_2025-01-06_tracker_200_2
    

    
    # 字串轉整數
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
    
    # send email if have signal
    handle_email(
                stock1, user_email,
                fastk_period, slowk_period, slowd_period, 
                fastperiod, slowperiod, signalperiod,
                bb_timeperiod, nbdevup, nbdevdn, matype,
                rsi_timeperiod, dmi_timeperiod
                )
          
    
    
    tracker_folder_path = r"/Users/chenyanjia/MyDjango/mydjango/finance/distance_method/monitor1/common1/tracker_results"
    # file_path = f"{tracker_folder_path}/{user}/{stock1}_{stock2}_{start_date}_{window_size}_{std}.json"
    
    # method = 'tracker'
    # window_size = 200
    # std = 2
    
    file_path = f"{tracker_folder_path}/{user}/{user}_{stock1}_{user_email}_{start_date}_{end_date}_{fastk_period}_{slowk_period}_{slowd_period}_{fastperiod}_{slowperiod}_{signalperiod}_{bb_timeperiod}_{nbdevup}_{nbdevdn}_{matype}_{rsi_timeperiod}_{dmi_timeperiod}.json"
    

        
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file) 
    else:
        data = inductor_tra(
            stock1, start_date, end_date, 
            fastk_period, slowk_period, slowd_period, 
            fastperiod, slowperiod, signalperiod,
            bb_timeperiod, nbdevup, nbdevdn, matype,
            rsi_timeperiod,
            dmi_timeperiod
        )
        print('addrss:', file_path)
        print('---------------------------------------------')
        

        
        # 將 JSON 資料保存到文件
        with open(f'{file_path}', 'w') as json_file:
            print('json:', json_file)
            print('---------------------------------------------')
            json.dump(data, json_file, indent=4) 
        
    return JsonResponse(data)

def inductor_tra(
    stock_inductor, start_date_inductor, end_date_inductor,
    fastk_period, slowk_period, slowd_period, 
    fastperiod, slowperiod, signalperiod,
    bb_timeperiod, nbdevup, nbdevdn, matype,
    rsi_timeperiod,
    dmi_timeperiod
    ):

    print('inductor backend')
    
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
        # print(timestamp)
        result_list.append(timestamp)
    
    # 蠟燭圖
    list_open                   = df_data['Open'].tolist()
    list_high                   = df_data['High'].tolist()
    list_low                    = df_data['Low'].tolist()
    list_adj_close              = df_data['Adj Close'].tolist()

    combined_list_candle        = [[date, open, high, low, adjclose] for date, open, high, low, adjclose in zip(result_list, list_open, list_high, list_low, list_adj_close)]

    combined_array_candle       = np.array(combined_list_candle) 

    data_stock_candle           = combined_array_candle.tolist()
    
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
        'bearish_engulfing_list'  : bearish_engulfing_list
    }

    return response

# 布林帶 
def band(
    stock_inductor, start_date_inductor, end_date_inductor,
    bb_timeperiod, nbdevup, nbdevdn, matype,
    ):
    
    print('in band method')
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

    print(break_upper_points)
    print(break_lower_points)

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
        # print(timestamp)
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

    return data_stock_Band_mid, data_stock_Band_upper, data_stock_Band_lower, data_stock_band_gc, data_stock_band_dc

# MACD指標
def macd(
    stock_inductor, start_date_inductor, end_date_inductor,
    fastperiod, slowperiod, signalperiod
    ):
    
    print('in macd method')
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
        # print(timestamp)
        macd_gc_result_list.append(timestamp)

    for date_str in macd_dcp_data_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        # print(timestamp)
        macd_dc_result_list.append(timestamp)


    data.reset_index(inplace=True)
    macd_data = data[['Date', 'MACD', 'Signal', 'Histogram']]
    data_date_str = macd_data["Date"].astype(str)
    macd_result_list = []

    for date_str in data_date_str:
        date_str = date_str.split(' ')[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
        # print(timestamp)
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
    
    # print(data_stock_MACD_fast, data_stock_MACD_slow, data_stock_MACD_hist, data_stock_MACD_fast_gc, data_stock_MACD_slow_dc)
    
    return data_stock_MACD_fast, data_stock_MACD_slow, data_stock_MACD_hist, data_stock_MACD_fast_gc, data_stock_MACD_slow_dc

# KD指標
def kd(
    stock_inductor, start_date_inductor, end_date_inductor,
    fastk_period, slowk_period, slowd_period,
    ):
    
    print('in kd method')
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
    
    return data_stock_K, data_stock_D, data_stock_K_gc, data_stock_D_dc

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
    
    # print('here', df['close'])
    
    # ------
    
    # 計算DMI
    high = df['high']
    low = df['low']
    close = df['close']
    # 計算 +DI, -DI 和 ADX
    # period = 14  # 通常的周期是 14
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
        # print(timestamp)
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
    # print(data_stock_dmi_gc)
    # print('-------------------')
    # print(data_stock_dmi_dc)
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
    # print(morning_star_dates)
    # print(red_3_dates)
    # print(bla_3_dates)
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
