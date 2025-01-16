import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from talib import abstract
import yfinance as yf
import talib
import pandas as pd
import datetime
# import warnings

# warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")


def send_email(message, recipient_email):
    # 設定寄件人和收件人
    sender_email = 'testsendemailforpy@gmail.com'  # 替換為你的 Gmail 地址
    sender_password = 'ebkv toeg xjjx nusa'  # 替換為你的 Gmail 應用專用密碼
    # recipient_email = 'jennybaby4wi@gmail.com'  # 替換為接收者的電子郵件地址

    # 建構郵件
    subject = "Signal Email"
    body = message
    email_message = MIMEMultipart()
    email_message['From'] = sender_email
    email_message['To'] = recipient_email
    email_message['Subject'] = subject
    email_message.attach(MIMEText(body, 'plain'))

    try:
        # 連接到 Gmail 的 SMTP 伺服器並發送郵件
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # 啟用加密
        server.login(sender_email, sender_password)  # 登錄
        server.sendmail(sender_email, recipient_email, email_message.as_string())  # 發送郵件
        print(f"Email sent successfully to {recipient_email}")
        server.quit()  # 結束連接
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def handle_email(
                stock, email,
                fastk_period, slowk_period, slowd_period, 
                fastperiod, slowperiod, signalperiod,
                bb_timeperiod, nbdevup, nbdevdn, matype,
                rsi_timeperiod, dmi_timeperiod
                ):

    current_date = datetime.date.today()
    # current_date = '2025-01-07'
    start_date = current_date - datetime.timedelta(days=120)
    # start_date = '2024-06-01'
    
    use_data=pd.DataFrame(yf.download(stock, start_date, current_date))
    t_date = use_data.index[-1].date()
    
    print(t_date)
    print('今天是 : ', current_date)
    
    if(t_date == current_date):
        kd_message = get_kd_signal(stock, start_date, current_date, fastk_period, slowk_period, slowd_period)
        if(kd_message):
            send_email(kd_message, email)
        else:
            print(f"{stock} : KD無信號")
            
        macd_message = get_macd_signal(stock, start_date, current_date, fastperiod, slowperiod, signalperiod)
        if(macd_message):
            send_email(macd_message, email)
        else:
            print(f"{stock} : MACD無信號")
        
        band_message = get_band_signal(stock, start_date, current_date, bb_timeperiod, nbdevup, nbdevdn, matype)
        if(band_message):
            send_email(band_message, email)
        else:
            print(f"{stock} : BAND無信號")       
        
        rsi_message = get_rsi_signal(stock, start_date, current_date, rsi_timeperiod)
        if(rsi_message):
            send_email(rsi_message, email)
        else:
            print(f"{stock} : RSI無信號")     
            
        adx_dmi_message = get_adx_dmi_signal(stock, start_date, current_date, dmi_timeperiod)
        if(adx_dmi_message):
            send_email(adx_dmi_message, email)
        else:
            print(f"{stock} : ADX_DMI無信號")   
    else:
        message = '沒有訊號!'
        send_email(message, email)

def get_kd_signal(stock, start_date, current_date, fastk_period, slowk_period, slowd_period):


    data=pd.DataFrame(yf.download(stock, start_date, current_date))
    
    print('-------------------- apple --------------------')
    print(data)
    print('-------------------- apple --------------------')

    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    high = data['High'].values
    low = data['Low'].values
    close = data['Close'].values

    # 計算 KD 指標
    fastk, fastd = talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)

    # 將計算的 K 線和 D 線加入到數據框中
    data['K'] = fastk
    data['D'] = fastd

    # 判斷今天和昨天的 K 線和 D 線值
    today_k = data['K'].iloc[-1]
    today_d = data['D'].iloc[-1]
    yesterday_k = data['K'].iloc[-2]
    yesterday_d = data['D'].iloc[-2]
    today_date = data.index[-1].date()
    

    
    print('today_date : ', today_date)

    # 判斷金叉
    if today_k > today_d and yesterday_k < yesterday_d:
        # print(f"KD金叉發生,日期 : {today_date} !")
        message = f"{stock} KD出現金叉訊號 - 日期 : {today_date}"
        return message
    # else:
    #     print("KD沒有金叉。")
        
    if today_k < today_d and yesterday_k > yesterday_d:
        # print(f"KD死叉發生,日期 : {today_date}!")
        message = f"{stock} KD出現死叉訊號 - 日期 : {today_date}"
        return message
    # else:
        # print("KD沒有死叉。")

    # 顯示數據，包括日期、K 和 D 值
    # print("日期\t\tK值\tD值")
    # for date, k, d in zip(data.index, data['K'], data['D']):
    #     print(f"{date.date()}\t{k:.2f}\t{d:.2f}")

    # 顯示今天和昨天的 K 和 D 值（可选）
    # print("\n今天的 K 值：", today_k)
    # print("今天的 D 值：", today_d)
    # print("昨天的 K 值：", yesterday_k)
    # print("昨天的 D 值：", yesterday_d)
    return


def get_macd_signal(stock, start_date, current_date, fastperiod, slowperiod, signalperiod):   

    data = pd.DataFrame(yf.download(stock, start_date, current_date))
    # data = yf.download('AAPL', start='2024-06-01', end='2024-12-31')

    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    close = data['Close']

    # 計算 MACD 指标
    macd, signal, hist = talib.MACD(close, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)

    # MACD, Signal, Histogram 加入到 DataFrame
    data['MACD'] = macd
    data['Signal'] = signal
    data['Histogram'] = hist

    # 取今天和昨天的 Histogram 值
    today_hist = data['Histogram'].iloc[-1]
    yesterday_hist = data['Histogram'].iloc[-2]
    today_date = data.index[-1].date()

    # 判断金叉或死叉
    if today_hist > 0 and yesterday_hist < 0:
        # print("MACD金叉發生!")
        # print(f"金叉發生！日期：{today_date}")
        message = f"{stock} MACD出現金叉訊號 - 日期 : {today_date}"
        return message
        
    if today_hist < 0 and yesterday_hist > 0:
        # print("MACD死叉發生!")
        # print(f"死叉發生！日期：{today_date}")
        message = f"{stock} MACD出現死叉訊號 - 日期 : {today_date}"
        return message
        
    # else:
    #     print("今天没有金叉或死叉。")
        
    return
        
    # for date, macd_value, signal_value, hist_value in zip(data.index, data['MACD'], data['Signal'], data['Histogram']):
    #     print(f"{date.strftime('%Y-%m-%d')}\t{macd_value:.2f}\t{signal_value:.2f}\t{hist_value:.2f}")


def get_band_signal(stock, start_date, current_date, bb_timeperiod, nbdevup, nbdevdn, matype):

    # 下载 AAPL 股票数据
    data = yf.download(stock, start_date, current_date)

    # 处理列名（如果是多层列名，则获取第一个层级）
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    # 计算布林通道
    upper_band, middle_band, lower_band = talib.BBANDS(data['Close'], timeperiod=bb_timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=matype)

    # 将布林通道的结果加入到 DataFrame
    data['UpperBand'] = upper_band
    data['MiddleBand'] = middle_band
    data['LowerBand'] = lower_band

    # 创建存储突破上轨和跌破下轨的天数的列表
    break_upper = []
    break_lower = []

    # 遍历数据，检测突破上轨和跌破下轨的天数
    for i in range(1, len(data)):
        today_close = data['Close'].iloc[i]
        yesterday_close = data['Close'].iloc[i - 1]

        today_upper = data['UpperBand'].iloc[i]
        yesterday_upper = data['UpperBand'].iloc[i - 1]

        today_lower = data['LowerBand'].iloc[i]
        yesterday_lower = data['LowerBand'].iloc[i - 1]

        # 判断是否突破上轨
        if today_close > today_upper and yesterday_close <= yesterday_upper:
            break_upper.append((data.index[i].date(), today_close))

        # 判断是否跌破下轨
        if today_close < today_lower and yesterday_close >= yesterday_lower:
            break_lower.append((data.index[i].date(), today_close))

    # 检测今天是否突破上轨或跌破下轨（保留原有功能）
    today_close = data['Close'].iloc[-1]
    yesterday_close = data['Close'].iloc[-2]

    today_upper = data['UpperBand'].iloc[-1]
    yesterday_upper = data['UpperBand'].iloc[-2]

    today_lower = data['LowerBand'].iloc[-1]
    yesterday_lower = data['LowerBand'].iloc[-2]
    
    today_date = data.index[-1].date()

    if today_close > today_upper and yesterday_close <= yesterday_upper:
        # print(f"突破上轨！日期：{data.index[-1].date()}，收盘价：{today_close}")
        message = f"{stock} 布林帶突破上軌訊號 - 日期 : {today_date}"
        return message
    if today_close < today_lower and yesterday_close >= yesterday_lower:
        # print(f"跌破下轨！日期：{data.index[-1].date()}，收盘价：{today_close}")
        message = f"{stock} 布林帶跌破下軌訊號 - 日期 : {today_date}"
        return message
    # else:
    #     print("今天没有突破上轨或跌破下轨。")

    # 打印所有历史突破记录
    # print("\n历史突破上轨的天数和收盘价：")
    # for date, close in break_upper:
    #     print(f"日期：{date}，收盘价：{close}")

    # print("\n历史跌破下轨的天数和收盘价：")
    # for date, close in break_lower:
    #     print(f"日期：{date}，收盘价：{close}")
    return

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


def get_rsi_signal(stock, start_date, current_date, rsi_timeperiod):

    df = pd.DataFrame(yf.download(stock, start_date, current_date))

    
    # 确保列名符合 TA-Lib 的要求
    df.rename(columns={
        "Adj Close": "adj_close",
        "Close": "close",
        "High": "high",
        "Low": "low",
        "Open": "open",
        "Volume": "volume"
    }, inplace=True)
    
    # 计算 RSI
    df["RSI"] = abstract.RSI(df, timeperiod=rsi_timeperiod)

    # 删除包含 NaN 的行
    df.dropna(subset=["RSI"], inplace=True)
    
    # 定義 RSI 上下界
    rsi_over = 80
    rsi_down = 20
    
    # 检测 RSI 穿越点
    df["RSI_Above_80"] = crossover(df["RSI"], pd.Series(rsi_over, index=df.index))
    df["RSI_Below_20"] = crossunder(df["RSI"], pd.Series(rsi_down, index=df.index))

    # 找出超买和超卖的日期
    overbuy = df[df["RSI_Above_80"]][["RSI"]]
    oversell = df[df["RSI_Below_20"]][["RSI"]]

    # 重置索引
    overbuy.reset_index(inplace=True)
    oversell.reset_index(inplace=True)

    # 判断当日 RSI 超买或超卖
    today_rsi = df["RSI"].iloc[-1]
    yesterday_rsi = df["RSI"].iloc[-2]
    today_date = df.index[-1].date()

    if yesterday_rsi < rsi_over and today_rsi > rsi_over:
        # print(f"超買！日期：{today_date},RSI:{today_rsi}")
        message = f"{stock} 出現RSI超買訊號 - 日期 : {today_date}"
        return message
    if yesterday_rsi > rsi_down and today_rsi < rsi_down:
        # print(f"超賣！日期：{today_date},RSI:{today_rsi}")
        message = f"{stock} 出現RSI超賣訊號 - 日期 : {today_date}"
        return message
    # else:
    #     print("今天無超買或超賣。")
    
    return

    # 打印历史超买和超卖的日期及 RSI 值
    # print("\n歷史超買记录:")
    # for _, row in overbuy.iterrows():
    #     print(f"日期：{row['Date'].date()},RSI:{row['RSI']}")

    # print("\n歷史超賣记录:")
    # for _, row in oversell.iterrows():
    #     print(f"日期：{row['Date'].date()},RSI:{row['RSI']}")


def get_adx_dmi_signal(stock, start_date, current_date, dmi_timeperiod):
    
    df = pd.DataFrame(yf.download(stock, start_date, current_date))

    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df.columns = [col.lower() for col in df.columns]

    # 計算指標
    period = 14  
    df["ADX"] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=dmi_timeperiod)
    df["DIP"] = talib.PLUS_DI(df['high'], df['low'], df['close'], timeperiod=dmi_timeperiod)
    df["DIM"] = talib.MINUS_DI(df['high'], df['low'], df['close'], timeperiod=dmi_timeperiod)


    # 判断金叉和死叉
    df["golden_cross"] = (df["DIP"].shift(1) < df["DIM"].shift(1)) & (df["DIP"] > df["DIM"])
    df["death_cross"] = (df["DIP"].shift(1) > df["DIM"].shift(1)) & (df["DIP"] < df["DIM"])

    # 篩選符合条件的金叉和死叉
    # golden_cross_df = df[(df["golden_cross"]) & (df["ADX"] > 20)]
    # death_cross_df = df[(df["death_cross"]) & (df["ADX"] > 20)]

    # 打印今天的金叉或死叉信息
    today = df.iloc[-1]  # 取最后一天数据
    today_date = df.index[-1].date() #本日日期
    
    if today["golden_cross"] and today["ADX"] > 20:
        # print(f"今天是金叉,ADX 值為 {today['ADX']:.2f}")
        message = f"{stock} 出現DMI金叉且ADX > 30 訊號 - 日期 : {today_date}"
        return message
    elif today["death_cross"] and today["ADX"] > 20:
        # print(f"今天是死叉,ADX 值為 {today['ADX']:.2f}")
        message = f"{stock} 出現DMI死叉且ADX > 30 訊號 - 日期 : {today_date}"
        return message

    # 输出所有金叉和死叉的日期
    # print("\n所有金叉的日期及ADX值:")
    # print(golden_cross_df[["ADX"]])

    # print("\n所有死叉的日期及ADX值:")
    # print(death_cross_df[["ADX"]])
    
    return



















































'''

def read_json_files():
    # 檢查資料夾是否存在
    TRACKER_DIR = "/Users/andrew/Documents/test.Django/Django_old/Lab_Training/common/tracker_results/andrew"
    if not os.path.exists(TRACKER_DIR):
        print(f"TRACKER_DIR {TRACKER_DIR} does not exist.")
        return

    # 初始化一個空的股票名稱列表
    user_data = []
    
    # current_date = '2025-01-05'
    current_date = datetime.date.today()
    start_date = current_date - datetime.timedelta(days=120)
    
    # 遍歷資料夾中的 JSON 文件
    for filename in os.listdir(TRACKER_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(TRACKER_DIR, filename)
            print(f"Reading file: {filename}")

            # 打開並讀取 JSON 文件
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)

            # 提取股票名稱（假設格式中股票名稱在文件名中，例如 "AAPL")
            user_name = filename.split("_")[0]  
            stock_name = filename.split("_")[1]
            gmail_name = filename.split("_")[2]
            start_date_name = filename.split("_")[3]
            end_date_name = filename.split("_")[4]
            method_name = filename.split("_")[5]
           

            # 將提取的信息組成一個列表並加入二維列表
            user_data.append([
                user_name, 
                stock_name, 
                gmail_name, 
                start_date_name, 
                end_date_name, 
                method_name
            ])

            
            # 打印內容
            # print(f"Stock Name: {stock_name}")
            # print(f"File Content: {json.dumps(data, indent=4)}")
            # print("-" * 50)
    for data in user_data:
        username, stock, email, start_date, end_date, type = data
        # print(stock)
        # print(email)
        
        kd_message = get_kd_signal(stock, start_date, current_date)
        if(kd_message):
            send_email(kd_message, stock, email)
        else:
            print(f"{stock} : KD無信號")
            
        macd_message = get_macd_signal(stock, start_date, current_date)
        if(macd_message):
            send_email(macd_message, stock, email)
        else:
            print(f"{stock} : MACD無信號")
        
        band_message = get_band_signal(stock, start_date, current_date)
        if(band_message):
            send_email(band_message, stock, email)
        else:
            print(f"{stock} : BAND無信號")       
        
        rsi_message = get_rsi_signal(stock, start_date, current_date)
        if(rsi_message):
            send_email(rsi_message, stock, email)
        else:
            print(f"{stock} : RSI無信號")     
            
        adx_dmi_message = get_adx_dmi_signal(stock, start_date, current_date)
        if(adx_dmi_message):
            send_email(adx_dmi_message, stock, email)
        else:
            print(f"{stock} : ADX_DMI無信號")   
            
    print(user_data)
    
# 調用函數查看 JSON 文件內容
read_json_files()

'''