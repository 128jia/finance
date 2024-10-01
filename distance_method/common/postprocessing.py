import json
import numpy as np
import pandas as pd
import yfinance as yf
from common import highchart_format 
from collections import defaultdict


def handle_signals_data(object, stock1, stock2, data1, data2):
    # stock price data
    plot_corr = pd.DataFrame({
        'date': data1.index,
        stock1: data1['Close'],
        stock2: data2['Close']
    })
    
    res = object.trading_signals
    sorted_list = sorted((res['upper'] + res['lower']), key=lambda x: x[0])
    plot_signals = defaultdict(list)   
    for row in sorted_list:
        date1 = highchart_format.convert_timestamp_to_highchart(row[0].strftime("%Y-%m-%d"))
        stock1_price1 = plot_corr.loc[row[0], stock1]
        stock2_price1 = plot_corr.loc[row[0], stock2]       
        
        if row[2]=="BUY":
            plot_signals["stock1_buy_point"].append([date1, stock1_price1]) 
            plot_signals["stock2_sell_point"].append([date1, stock2_price1])
        elif row[2]=="SELL":
            plot_signals["stock1_sell_point"].append([date1, stock1_price1]) 
            plot_signals["stock2_buy_point"].append([date1, stock2_price1]) 
        if row[3]=="Open":
            plot_signals["Entry_Exit"].append({ "date": date1, "color": 'pink', "label": 'entry'})
        elif row[3]=="Close":
            plot_signals["Entry_Exit"].append({ "date": date1, "color": 'gray', "label": 'exit'})

    table_signals = []
    for row in sorted_list:
        stock1_price1 = round(plot_corr.loc[row[0].strftime("%Y-%m-%d"), stock1], 2)
        stock2_price1 = round(plot_corr.loc[row[0].strftime("%Y-%m-%d"), stock2], 2)     
        if row[2]=="BUY":
            table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock1_action": "BUY", "stock1_price":stock1_price1, "stock2_action":"SELL", "stock2_price":stock2_price1, "type":row[3]})
        elif row[2]=="SELL":
            table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock1_action":"SELL", "stock1_price":stock1_price1, "stock2_action":"BUY", "stock2_price":stock2_price1, "type":row[3]})

    return plot_signals, table_signals

def handle_bollinger_band_data(object):
    sorted_list = sorted((object.trading_signals['upper'] + object.trading_signals['lower']), key=lambda x: x[0])
    spread = object.spread.dropna()
    spread = spread.reset_index()
    spread = spread.values.tolist()
    spread = [[int(date.timestamp() * 1000), val] for date, val in spread]
    middle_line = object.rolling_mean.dropna()
    middle_line = middle_line.reset_index()
    middle_line = middle_line.values.tolist()
    middle_line = [[int(date.timestamp() * 1000), val] for date, val in middle_line]
    upper_line = object.upper_line.dropna()
    upper_line = upper_line.reset_index()
    upper_line = upper_line.values.tolist()
    upper_line = [[int(date.timestamp() * 1000), val] for date, val in upper_line]
    lower_line = object.lower_line.dropna()
    lower_line = lower_line.reset_index()
    lower_line = lower_line.values.tolist()
    lower_line = [[int(date.timestamp() * 1000), val] for date, val in lower_line]
    bands_signals_sell = [[int(ele[0].timestamp() * 1000), ele[1]] for ele in sorted_list if ele[2]=='SELL']
    bands_signals_buy = [[int(ele[0].timestamp() * 1000) , ele[1]] for ele in sorted_list if ele[2]=='BUY']
    
    return spread, middle_line, upper_line, lower_line, bands_signals_sell, bands_signals_buy

def handle_profit_loss_data(object):
    pl_daily_profits = [[int(date.timestamp() * 1000), val] for date, val in object.daily_profits]
    pl_total_values = [[int(date.timestamp() * 1000), val] for date, val in object.total_values]
    pl_entry_point = [[int(date.timestamp() * 1000), val] for date, val in object.entry_point]
    pl_exit_point = [[int(date.timestamp() * 1000), val] for date, val in object.exit_point]
    
    return pl_daily_profits, pl_total_values, pl_entry_point, pl_exit_point
