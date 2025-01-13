import twstock

ticker = "2330"
stock_info = twstock.realtime.get(ticker)

if stock_info["success"]:
    # 檢查返回的數據是否包含 "nf" 鍵
    if "nf" in stock_info["realtime"]:
        print(f"股票名稱: {stock_info['realtime']['nf']}")
    else:
        print("返回數據中缺少 'nf' 鍵，請檢查 API 是否正常。")
else:
    print("無法取得即時股票數據。請檢查 API 是否正常運行或股票代碼是否正確。")
