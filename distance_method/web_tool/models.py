from django.db import models
import json
# Create your models here.

class StrategyResult(models.Model):
    # 股票資訊
    stock1 = models.CharField(max_length=10)  # 第一支股票代號
    stock2 = models.CharField(max_length=10)  # 第二支股票代號
    
    # 策略參數
    start_date = models.DateField(null=False)  # 策略執行的開始日期
    end_date = models.DateField(null=False)  # 策略執行的結束日期
    window_size = models.IntegerField()  # 移動平均的窗口大小
    n_times = models.IntegerField()  # 標準差倍數
    
    # 每日股票價格和交易信號
    date = models.DateField()  # 資料的日期
    stock1_close = models.FloatField()  # 股票1的收盤價
    stock2_close = models.FloatField()  # 股票2的收盤價
    spread = models.FloatField()  # 股票1與股票2之間的spread
    action = models.CharField(max_length=100, blank=True, null=True)  # 買賣動作，如 'SELL' 或 'BUY' (可選)
    status = models.CharField(max_length=100, blank=True, null=True)  # 開關倉狀態，如 'Open' 或 'Close' (可選)
    
    # 損益結果 (可選)
    final_value = models.FloatField(blank=True, null=True)  # 最終總資金
    profit_percent = models.FloatField(blank=True, null=True)  # 收益率百分比
    daily_value = models.TextField(blank=True, null=True)  # 每日損益 (存為字符串)
    
    def __str__(self):
        return f"StrategyResult: {self.stock1} vs {self.stock2} on {self.date}" 

    def __str__(self):
        return f"StrategyResult: {self.stock1} vs {self.stock2} on {self.date}"
    
    def set_daily_value(self, daily_value_dict):
        """將每日損益字典轉換為字符串並存儲"""
        self.daily_value = json.dumps(daily_value_dict)

    def get_daily_value(self):
        """將存儲的每日損益字符串轉換回字典"""
        if self.daily_value:
            return json.loads(self.daily_value)
        return {}