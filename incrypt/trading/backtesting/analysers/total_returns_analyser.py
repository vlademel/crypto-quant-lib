import backtrader as bt
from collections import OrderedDict


class TotalReturns(bt.Analyzer):
    '''This analyzer reports the total pnl for strategy

    Params:

      - timeframe (default: ``None``)
        If ``None`` then the timeframe of the 1st data of the system will be
        used

      - compression (default: ``None``)

        Only used for sub-day timeframes to for example work on an hourly
        timeframe by specifying "TimeFrame.Minutes" and 60 as compression

        If ``None`` then the compression of the 1st data of the system will be
        used

    Methods:

      - get_analysis

        Returns a dictionary with returns as values and the datetime points for
        each return as keys
    '''

    def __init__(self):
        self.total_pnl = 0
        self.unrealized = 0  # Unrealized pnl for all positions all strategies
        self.positions = OrderedDict.fromkeys([d._name or 'Data%d' % i
                                               for i, d in enumerate(self.datas)], 0)  # Current strategy positions

    def start(self):
        tf = min(d._timeframe for d in self.datas)
        self._usedate = tf >= bt.TimeFrame.Days

    def notify_order(self, order):

        if order.status in [order.Completed, order.Partial]:
            self.total_pnl += order.executed.pnl - order.executed.comm

            self.positions[order.data] += order.executed.size

    def next(self):
        if self._usedate:
            self.rets[self.strategy.datetime.date()] = self.total_pnl
        else:
            self.rets[self.strategy.datetime.datetime()] = self.total_pnl

    def stop(self):

        for dname in self.positions:
            self.unrealized += (self.strategy.dnames[dname].close[0] -
                                self.strategy.positionsbyname[dname].price) * \
                               self.strategy.positionsbyname[dname].size