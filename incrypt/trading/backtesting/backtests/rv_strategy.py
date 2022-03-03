import backtrader as bt
import logging

from incrypt.trading.backtesting.data import DailyCoinBacktraderData
from incrypt.trading.backtesting.multi_trade_observer import MTradeObserver
from incrypt.trading.backtesting.indicators.zscore_ind import ZScoreInd
from incrypt.trading.backtesting.fractional_commission import CommInfoFractional

class TestStrategy(bt.Strategy):

    params = dict(
        printout=False,
        onlylong=False,
        mtrade=False,
        target=0.2
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.signal = ZScoreInd(self.datas[0],
                                self.datas[1],
                                subplot=True,
                                window=30)

        self.order = None

    def next(self):
        self.current_trade = 0

        if ((self.signal >= 4) & (self.current_trade!=2)):
            if self.position:
                self.log('CLOSE SHORT , %.2f' % self.datas[1].close[0])
                self.close(self.datas[1])
                self.log('CLOSE LONG , %.2f' % self.datas[0].close[0])
                self.close(self.datas[0])
            self.log('BUY CREATE , %.2f' % self.datas[1].close[0])
            self.order_target_percent(data=self.datas[1], target=self.p.target)
            self.log('SELL CREATE , %.2f' % self.datas[0].close[0])
            self.order_target_percent(data=self.datas[0], target=-self.p.target)
            self.current_trade = 2
        elif ((self.signal <= -4) & (self.current_trade!=1)):
            if self.position:
                self.log('CLOSE SHORT , %.2f' % self.datas[0].close[0])
                self.close(self.datas[0])
                self.log('CLOSE LONG , %.2f' % self.datas[1].close[0])
                self.close(self.datas[1])
            self.log('BUY CREATE , %.2f' % self.datas[0].close[0])
            self.order_target_percent(data=self.datas[0], target=self.p.target)
            self.log('SELL CREATE , %.2f' % self.datas[1].close[0])
            self.order_target_percent(data=self.datas[1], target=-self.p.target)
            self.current_trade = 1

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED/SUBMITTED', dt=order.created.dt)
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

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('NOT EXECUTED, REASON: {0!s}'.format(order.status))

        # Sentinel to None: new orders allowed
        self.order = None

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
    cerebro.addstrategy(TestStrategy)
    eth = DailyCoinBacktraderData('2018-01-01','2020-12-31','eth').data
    btc = DailyCoinBacktraderData('2018-01-01','2020-12-31', 'btc').data
    # Add the Data Feed to Cerebro
    cerebro.adddata(eth)
    cerebro.adddata(btc)
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    cerebro.broker.addcommissioninfo(CommInfoFractional())
    # Add the MultiTradeObserver
    cerebro.addobserver(MTradeObserver)
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Run over everything
    cerebro.run()
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()
