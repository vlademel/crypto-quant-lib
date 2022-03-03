import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt

from incrypt.trading.backtesting.data import DailyCoinBacktraderData
from incrypt.trading.backtesting.multi_trade_observer import MTradeObserver
from incrypt.trading.backtesting.fractional_commission import CommInfoFractional
from trading.research.data.daily_coin_price_data import AllTickerData
from incrypt.trading.backtesting.analysers.trade_close_analyser import TradeClosed


class SimpleMomentumStrategy(bt.Strategy):
    params = dict(
        printout=False,
        onlylong=False,
        mtrade=False,
        target=0.05
    )

    def prenext(self):
        self.next()

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.tickers = AllTickerData('2019-01-01', '2019-12-31', min_len=5).data
        self.order = None
        self.open_position = False
        self.bar_executed = 0

    def next(self):
        print(self.datetime.date(ago=0))
        self.duration = len(self) - self.bar_executed + 1
        tickers = self.calculate_returns()

        if self.open_position:
            if self.duration >= 1:
                # print("Conditions met...")
                self.close_positions()
                self.open_positions(tickers)
        else:
            # print("Conditions not met...")
            self.open_position = True
            self.open_positions(tickers)

    def calculate_returns(self):
        n = len(self.tickers) - 1
        rtn_ls = []
        for i in range(n):
            rtn = (self.datas[i].close[0] / self.datas[i].close[-1]) - 1
            rtn_ls.append((i, rtn))
        sorted_rtns = sorted(rtn_ls, key=lambda tup: tup[1], reverse=True)
        tickers = [i[0] for i in sorted_rtns if i[1] < -0.10]
        # print(tickers)
        return tickers

    def close_positions(self):
        for data in self.datas:
            size = self.getposition(data).size
            if size != 0:
                self.close(data)

    def open_positions(self, tickers):
        for ticker in tickers:
            self.log('BUY CREATE, %.2f' % self.datas[ticker].close[0])
            self.order_target_percent(data=self.datas[ticker], target=self.p.target)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            # self.log('ORDER ACCEPTED/SUBMITTED', dt=order.created.dt)
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED')

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Size: %.4f Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.size,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            else:  # Sell
                self.log('SELL EXECUTED, Size: %.4f Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.size,
                          order.executed.price,
                          order.executed.value,
                          order.executed.comm))

        elif order.status in [order.Canceled]:
            self.log('NOT EXECUTED, REASON: CANCELED')
        elif order.status in [order.Margin]:
            self.log('NOT EXECUTED, REASON: MARGIN')
        elif order.status in [order.Rejected]:
            self.log('NOT EXECUTED, REASON: REJECTED')

        # Sentinel to None: new orders allowed
        self.order = None
        self.bar_executed = len(self)

    def notify_trade(self, trade):
        if trade.isclosed:
            print("--------------------------------------")
            self.log('TRADE PROFIT, GROSS %.2f, NET %.2f' %
                     (trade.pnl, trade.pnlcomm))
            print("--------------------------------------")
        elif trade.justopened:
            self.log('TRADE OPENED, SIZE %.2f' % trade.size)

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    # Add a strategy
    cerebro.addstrategy(SimpleMomentumStrategy)
    start_date, end_date = '2019-01-01', '2019-12-31'
    all_data = DailyCoinBacktraderData(start_date, end_date, min_len=5).data
    for data in all_data:
        cerebro.adddata(data)
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    cerebro.broker.addcommissioninfo(CommInfoFractional())
    cerebro.addanalyzer(TradeClosed, _name="trade_closed")
    # cerebro.addanalyzer(TotalReturns, _name="tr")
    # Add the MultiTradeObserver
    cerebro.addobserver(MTradeObserver)
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Run over everything
    strategy = cerebro.run(runonce=False)
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()

    stats = strategy[0].analyzers.trade_closed.rets
    data = []
    for key, item in stats.items():
        data.append([item[0], item[2]])
    df = pd.DataFrame(data=data, columns=['date', 'pnl']).set_index('date')
    plt.plot(df.cumsum())
