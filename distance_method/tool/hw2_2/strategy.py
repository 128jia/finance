import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (
        ('short_rsi', 5),  # 短期RSI的默认参数
        ('long_rsi', 20),  # 長期RSI的默认参数
    )

    def __init__(self):
        # 获取数据的引用
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        
        # 初始化订单变量以跟踪未完成订单
        self.order = None

        # 初始化技术指标
        self.rsi_short = bt.indicators.RSI(self.dataclose, period=self.params.short_rsi)
        self.rsi_long = bt.indicators.RSI(self.dataclose, period=self.params.long_rsi)

    def log(self, txt, dt=None):
        '''输出日志'''
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return  # 如果订单已经提交或接受，返回不做任何处理

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm: {order.executed.comm}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm: {order.executed.comm}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # 清除订单
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')

    def next(self):
        # 检查是否有未完成的订单
        if self.order:
            return

        # 检查是否持有头寸
        if not self.position:
            # 定义进场条件：当短期RSI大于长期RSI时，买入
            if self.rsi_short[0] > self.rsi_long[0]:
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
                self.order = self.buy()

        else:
            # 定义出场条件：当短期RSI小于长期RSI * 0.999 时，卖出
            if self.rsi_short[0] < self.rsi_long[0] * 0.999:
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.order = self.sell()
