import backtrader as bt

from incrypt.trading.backtesting.data import DailyCoinBacktraderData
from incrypt.trading.backtesting.indicators.zscore_ind import ZScoreInd

class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose_eth = self.datas[0].close
        self.dataclose_btc = self.datas[1].close

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('ETH Close, %.2f' % self.dataclose_eth[0])
        self.log('BTC Close, %.2f' % self.dataclose_btc[0])


        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if ZScoreInd(data0=self.dataclose_btc, data1=self.dataclose_eth) >= 3:
                self.log('BUY CREATE, %.2f' % self.dataclose_eth[0])
                self.log('SELL CREATE, %.2f' % self.dataclose_btc[0])
                self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    eth = DailyCoinBacktraderData('2020-01-01','2020-02-01','eth').data
    btc = DailyCoinBacktraderData('2020-01-01', '2020-02-01', 'btc').data

    # Add the Data Feed to Cerebro
    cerebro.adddata(eth)
    cerebro.adddata(btc)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()
