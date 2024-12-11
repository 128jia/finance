from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from collections import defaultdict
from itertools import permutations
from datetime import datetime
import json,traceback,logging
import numpy as nps
import pandas as pd
import yfinance as yf
from django.contrib import messages
from common import highchart_format 
from common.strategy import Distance_method
from common.postprocessing import handle_signals_data, handle_bollinger_band_data, handle_profit_loss_data, handle_exe_signals_data
from common.postprocessing import handle_api_signals_data, handle_api_bollinger_band_data, handle_api_profit_loss_data, handle_api_exe_signals_data
#from tool.models import StrategyResult
from tool.hw2.rsi_cross_strategy import rsi_cross_strategy
from tool.hw2.BackTest import Performance
from tool.hw2_2.strategy import MyStrategy
import backtrader as bt
from .hw10.utils import PerRiver 
from django.views.decorators.csrf import ensure_csrf_cookie

def web(request):
    if not request.user.is_authenticated:
        messages.success(request, 'Sorry ! Please Log In.')
        return redirect("http://127.0.0.1:1984/account/login")
    return (render(request,"base.html"))

def ScreenerDistance(request):
    stock1 = request.POST.get("stock1")
    stock2 = request.POST.get("stock2")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    window_sizes = request.POST.get("window_sizes")
    std = int(request.POST.get("std"))
    
    # yahoo database
    data1_response = yf.download(stock1, start=start_date, end=end_date)
    if data1_response is not None:
        data1_his = highchart_format.yahoo_convert_quote_series(data1_response)
    data2_response = yf.download(stock2, start=start_date, end=end_date)
    if data2_response is not None:
        data2_his = highchart_format.yahoo_convert_quote_series(data2_response)   
        
        
    # Communicate with function api
    from common.func_client import  FuncClient
    fc = FuncClient()
    params = {
        'stock1' : str(stock1),
        'stock2' : str(stock2),
        'start_date' : str(start_date),
        'end_date' : str(end_date),
        'window_size' : int(window_sizes),
        'n_times' : int(std)
    }
    res = fc.pairtrading_backtesting(params=params, method="distance")
    # Handle signals data
    plot_signals, table_signals = handle_api_signals_data(object = res, 
                                        stock1 = stock1, 
                                        stock2 = stock2, 
                                        data1 = data1_response, 
                                        data2 = data2_response)
    
    # Handle Bollinger Bands data
    spread, middle_line, upper_line, lower_line, bands_signals_sell, bands_signals_buy = handle_api_bollinger_band_data(object = res)
    
    # Handle Profit_loss data
    pl_daily_profits, pl_total_values, pl_entry_point, pl_exit_point = handle_api_profit_loss_data(object = res)
    
    # Handle execution signals data
    exe_table_signals = handle_api_exe_signals_data(object = res, 
                                                    stock1 = stock1, 
                                                    stock2 = stock2, 
                                                    data1 = data1_response, 
                                                    data2 = data2_response)

    response = {
        'stock1': stock1, 
        'stock2': stock2, 
        'data1_his': data1_his, 
        'data2_his': data2_his,
        'plot_signals': plot_signals,
        'exe_table_signals':exe_table_signals,
        'table_signals': table_signals,
        'spread' : spread,
        'middle_line' : middle_line,
        'upper_line' : upper_line,
        'lower_line' : lower_line,
        'bands_signals_sell' : bands_signals_sell,
        'bands_signals_buy' : bands_signals_buy,
        'pl_daily_profits' : pl_daily_profits,
        'pl_total_values' : pl_total_values,
        'pl_entry_point' : pl_entry_point,
        'pl_exit_point' : pl_exit_point
    }
    
    return JsonResponse(response)




    # object = Distance_method(
    #     stock1 = str(stock1), 
    #     stock2 = str(stock2), 
    #     start_date = str(start_date), 
    #     end_date = str(end_date), 
    #     window_size = int(window_sizes), 
    #     n_times = int(std)
    #     )
    # object.run()
    # # Handle signals data
    # plot_signals, table_signals = handle_signals_data(object = object, 
    #                                     stock1 = stock1, 
    #                                     stock2 = stock2, 
    #                                     data1 = data1_response, 
    #                                     data2 = data2_response)
    
    # # Handle Bollinger Bands data
    # spread, middle_line, upper_line, lower_line, bands_signals_sell, bands_signals_buy = handle_bollinger_band_data(object = object)
    
    # # Handle Profit_loss data
    # pl_daily_profits, pl_total_values, pl_entry_point, pl_exit_point = handle_profit_loss_data(object = object)
    
    # # Handle execution signals data
    # exe_table_signals = handle_exe_signals_data(object = object, 
    #                                                 stock1 = stock1, 
    #                                                 stock2 = stock2, 
    #                                                 data1 = data1_response, 
    #data2 = data2_response)
#hw2-1
@ensure_csrf_cookie
def rsi_cross_ajax(request):
    print("step1:action")
    if request.method == 'POST':
        try:
            # 從前端獲取表單數據
            
            stock = request.POST.get('stock')
            short_rsi = int(request.POST.get('short_rsi'))
            long_rsi = int(request.POST.get('long_rsi'))
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            print(f"Stock: {stock}, Start: {start_date}, End: {end_date}, Short RSI: {short_rsi}, Long RSI: {long_rsi}")
            # 將字符串形式的日期轉換為 datetime 對象
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # 執行 RSI 黃金交叉策略
            data, trade = rsi_cross_strategy(stock, start_date, end_date, short_rsi, long_rsi)

            # 確認 trade 有數據
            if trade is None or trade.empty:
                return JsonResponse({'success': False, 'error': 'No trade data available'}, status=400)

            # 調用 backtest.py 中的 Performance 函數來計算交易績效
            trade1 = Performance(trade)

            if trade1 is None:
                return JsonResponse({'error': 'No trade data available'}, status=400)
            # 手動計算 profit (賣出價格 - 買入價格)
            trade1['profit'] = trade1['cover_price'] - trade1['order_price']
            trade1['cumulative_profit'] = trade1['profit'].cumsum()

            # 這些欄位需要在 views.py 內手動計算，因為 Performance 中沒有提供
            total_return = round(trade1['ret'].sum(), 4)
            trade_count = trade1.shape[0]
            average_return = round(trade1['ret'].mean(), 4)

            # 計算平均持有天數
            onopen_day = (trade1['cover_time'] - trade1['order_time']).mean().days

            # 計算勝率、賺賠比等指標
            earn_trade = trade1[trade1['ret'] > 0]
            loss_trade = trade1[trade1['ret'] <= 0]
            earn_ratio = earn_trade.shape[0] / trade1.shape[0] if trade1.shape[0] > 0 else 0
            avg_earn = earn_trade['ret'].mean() if not earn_trade.empty else 0
            avg_loss = loss_trade['ret'].mean() if not loss_trade.empty else 0
            win_rate = round(earn_ratio, 2)
            risk_reward_ratio = abs(avg_earn / avg_loss)
            expectancy = round(((earn_ratio * risk_reward_ratio) - (1 - earn_ratio)), 4)

            # 計算獲利和虧損的平均持有天數
            earn_onopen_day = (earn_trade['cover_time'] - earn_trade['order_time']).mean().days
            loss_onopen_day = (loss_trade['cover_time'] - loss_trade['order_time']).mean().days

            # 最大連續虧損
            tmp_accloss = 1
            max_accloss = 1
            for ret in trade1['ret'].values:
                if ret <= 0:
                    tmp_accloss *= ret
                    max_accloss = min(max_accloss, tmp_accloss)
                else:
                    tmp_accloss = 1
            max_consecutive_loss = round(max_accloss, 4)

            # 最大回撤
            max_drawdown = round(1 - trade1['dd'].min(), 4)

            # 準備傳遞到前端的績效數據
            performance_data = {
                'total_return': total_return,
                'trade_count': trade_count,
                'average_return': average_return,
                'average_hold_days': onopen_day,
                'win_rate': win_rate,
                'average_profit': round(avg_earn, 4),
                'average_loss': round(avg_loss, 4),
                'risk_reward_ratio': round(risk_reward_ratio, 4),
                'expectancy': expectancy,
                'profit_avg_hold_days': earn_onopen_day,
                'loss_avg_hold_days': loss_onopen_day,
                'max_consecutive_loss': max_consecutive_loss,
                'max_drawdown': max_drawdown
            }

            # 準備報酬率和最大回撤走勢數據
            profit_mdd_data = []
            for i in range(len(trade1)):
                timestamp = trade1['cover_time'].iloc[i]
                if pd.isna(timestamp):  # 檢查是否是NaT，跳過這些值
                    continue
                profit_mdd_data.append({
                    'date': int(timestamp.timestamp()) * 1000,  # 日期轉毫秒
                    'profit': round(trade1['acc_ret'].iloc[i], 4),
                    'dd': round(trade1['dd'].iloc[i], 4)
                })

            # 準備 OHLC 和成交量數據
            data['Timestamp'] = data.index
            data['Timestamp'] = data['Timestamp'].apply(lambda x: int(x.timestamp()) * 1000)
            ohlc_list = data[['Timestamp', 'open', 'high', 'low', 'close']].values.tolist()
            volume_list = data[['Timestamp', 'volume']].values.tolist()

            # 準備交易結果數據
            trade_results = []
            buy_dates = []
            sell_dates = []
            for i, row in trade1.iterrows():
                buy_date = row['order_time']
                sell_date = row['cover_time']
                if pd.isna(buy_date) or pd.isna(sell_date):
                    continue  # 如果沒有買入或賣出時間，跳過這筆交易
                trade_results.append({
                    'buy_sell': row['bs'],
                    'buy_date': buy_date.strftime('%Y-%m-%d'),
                    'buy_price': row['order_price'],
                    'sell_date': sell_date.strftime('%Y-%m-%d'),
                    'sell_price': row['cover_price'],
                    'trade_units': row['order_unit'],
                    'profit': row['profit'],
                    'cumulative_profit': row['cumulative_profit']
                })
                buy_dates.append(buy_date.strftime('%Y-%m-%d'))
                sell_dates.append(sell_date.strftime('%Y-%m-%d'))
            # 回傳數據到前端
            return JsonResponse({
                'trade_results': trade_results,
                'profit_mdd_data': profit_mdd_data,
                'ohlc': ohlc_list,
                'volume': volume_list,
                'buy_dates': buy_dates,
                'sell_dates': sell_dates,
                'performance_data': performance_data
            })

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


# hw2-2
def run_strategy(request):
    try:
        # 從前端獲取數據
        
        stock1 = request.POST.get('stock')
        print("---------------------",stock1)
        order_units = int(request.POST.get('order_units'))
        short_rsi = int(request.POST.get('short_rsi'))
        long_rsi = int(request.POST.get('long_rsi'))
        capital = float(request.POST.get('capital'))
        fee = float(request.POST.get('fee'))
        start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')
        print(f"stock:{stock1},unit:{order_units},rsi{short_rsi}、{long_rsi},cpital:{capital},fee:{fee},start:{start_date},end date:{end_date}")
        # 初始化 Cerebro 回測系統
        cerebro = bt.Cerebro()

        # 添加策略到回測系統
        cerebro.addstrategy(MyStrategy, short_rsi=short_rsi, long_rsi=long_rsi)

        # 使用 yfinance 下載股票數據
        data = bt.feeds.PandasData(dataname=yf.download(f'{stock1}.TW', start=start_date, end=end_date))
        cerebro.adddata(data)

        # 設定初始資產和手續費和買進股數
        cerebro.broker.setcash(capital)
        cerebro.broker.setcommission(commission=fee / 100)  # 百分比轉為小數
        cerebro.addsizer(bt.sizers.FixedSize, stake = order_units)

        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe = bt.TimeFrame.Years, _name = 'Timereturn')
        cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name = 'AnnualReturn')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio', riskfreerate=0.2)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
        cerebro.addanalyzer(bt.analyzers.Returns, _name= 'returns')
        cerebro.addanalyzer(bt.analyzers.Transactions, _name= 'transactions')

        # 執行策略
        result = cerebro.run()
        # try:
        #     result = cerebro.run()
        # except ZeroDivisionError:
        #     print("ZeroDivisionError occurred in run_strategy.")

        # 提取結果
        timereturn = result[0].analyzers.Timereturn.get_analysis()
        annualreturn = result[0].analyzers.AnnualReturn.get_analysis()
        sharpe_ratio = result[0].analyzers.SharpeRatio.get_analysis()
        drawdown = result[0].analyzers.DrawDown.get_analysis()
        trade_analysis = result[0].analyzers.trade_analyzer.get_analysis()
        returns = result[0].analyzers.returns.get_analysis()
        transactions = result[0].analyzers.transactions.get_analysis()
        # print(transactions)  # 這可以幫助檢查 transactions 的具體結構
        # 確認每個交易記錄包含正確的欄位，並轉換為字典列表供前端 DataTable 顯示
        transaction_list = []
        for date, transaction_data in transactions.items():
            for transaction in transaction_data:
                transaction_list.append({
                    'date': date.isoformat(),  # 直接使用 date 的 iso 格式
                    'amount': transaction[0],  # 第一個元素是交易數量
                    'price': transaction[1],  # 第二個元素是交易價格
                    'value': transaction[4]   # 第五個元素是交易價值
            })

        # 將 datetime.date 對象轉為字串，避免 JSON 轉換錯誤
        annualreturn = {str(key): value for key, value in annualreturn.items()}
        timereturn = {str(key): value for key, value in timereturn.items()}

        # 計算期末資產
        final_value = cerebro.broker.getvalue()

        # 傳回結果給前端
        return JsonResponse({
            'initial_cash': capital,
            'final_cash': round(final_value, 2),
            'sharpe_ratio': round(sharpe_ratio.get('sharperatio', 0), 2),  # 如果沒有sharpe_ratio，設為0
            'max_drawdown': f"{round(drawdown.get('max', {}).get('drawdown', 0), 2)}%",  # 防止缺少數據時出錯
            'time_return': timereturn, 
            'annual_return': annualreturn,
            'trade_analysis': trade_analysis,
            'returns': returns,
            'transactions': transaction_list
        })

    except Exception as e:
        # 打印錯誤日誌
        print(f"Error in run_strategy: {str(e)}")
        traceback.print_exc()  # 打印完整的錯誤跟蹤
        return JsonResponse({'error': str(e)}, status=500)

def web_tracker(request):
    # render search page
    if not request.user.is_authenticated:
        messages.success(request, 'Sorry ! Please Log In.')
        return redirect('/account/login')
    return (render(request, 'tracker.html'))

#hw10
logger = logging.getLogger(__name__)

@csrf_exempt
def get_per_river_data(request):
    if request.method == 'POST':
        try:
            # 獲取 POST 請求中的參數
            body = json.loads(request.body)
            stock_code = body.get("stockCode")
            time_unit = body.get("timeUnit").upper()  # 轉換為大寫（符合 PerRiver 類別要求）
            if time_unit == "QUARTER":
                time_unit = "QUAR"  # 將 quarter 替換為 quar
            print("時間單位",time_unit)
            # 確保參數完整
            if not stock_code or not time_unit:
                return JsonResponse({"error": "Missing parameters"}, status=400)

            # 調用 PerRiver 類別處理數據
            per_river = PerRiver()
            result = per_river.run(stock_code, time_unit)
            print("here 是結果喔",result)
            return JsonResponse(result)

        except Exception as e:
            logger.error("發生錯誤: %s", str(e))
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)
