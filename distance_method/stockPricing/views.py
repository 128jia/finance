from django.http import JsonResponse
from django.shortcuts import render
from .hw9 import PricingStrategy  # 匯入您的 PricingStrategy 類別
 
def stock_pricing_view(request):
    if request.method == "POST":
        print("POST request received")
        ticker = request.POST.get("ticker") 
        year = request.POST.get("years")
        print(f"Ticker: {ticker}, Year: {year}")
    
        try:
            # 創建 PricingStrategy 實例
            strategy = PricingStrategy(ticker, int(year))

            # 執行定價策略
            result = strategy.run()

            # 整理數據返回前端
            response_data = {
                "current_price": result["NewPrice"],
                "intervals": {
                    "down_cheap": result["down_cheap"],
                    "cheap_reasonable": result["cheap_reasonable"],
                    "reasonable_expensive": result["reasonable_expensive"],
                    "up_expensive": result["up_expensive"],
                },
                "valuations": {
                    "cheap": result["cheap"],
                    "reasonable": result["reasonable"],
                    "expensive": result["expensive"],
                },
                "tables": {
                    "dividend_table": result["dividend_table"]["data"][:int(year)],
                    "high_low_table": result["high_low_table"]["data"][:int(year)],
                    "PER_table": result["PER_table"]["data"][:int(year)],
                    "PBR_table": result["PBR_table"]["data"][:int(year)],
                }               
            }
            print("New Price:", response_data["current_price"])
            return JsonResponse(response_data, safe=False)

        except Exception as e:
            print(f"Error processing request: {e}")  # 打印詳細錯誤
            # 返回錯誤訊息
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "stock_pricing.html")  # 渲染模板
