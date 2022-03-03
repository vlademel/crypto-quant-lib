import backtrader as bt

class ZScoreInd(bt.Indicator):

    _mindatas = 2
    params = (('window', 50),
              ('score_threshold', 3))
    lines = ('signal',)
    plotinfo = dict(plotymargin=0.15)
    plotlines = dict(signal=dict(ls='-'))

    def __init__(self):
        returns_1 = bt.ind.PercentChange(self.datas[0], period=1)
        returns_2 = bt.ind.PercentChange(self.datas[1], period=1)
        ratio = returns_1 / returns_2
        spread_mean = bt.ind.SMA(ratio, period=self.p.window)
        spread_std = bt.ind.StdDev(ratio, period=self.p.window)
        # signal = (ratio - spread_mean) / spread_std
        # if signal >= self.score_threshold:
        #     self.l.signal = 1
        # elif signal < self.score_threshold:
        #     self.l.signal = -1
        self.l.signal = (ratio - spread_mean) / spread_std
