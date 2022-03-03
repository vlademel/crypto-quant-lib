from incrypt.trading.research.daily_mean_reversion_base import DailyMeanReversionBase

import pandas as pd

class DailyMeanReversionTicker(DailyMeanReversionBase):
    def __init__(self,
                 t,
                 n,
                 filter,
                 start_date=None,
                 end_date=None):
        '''
        :param t: how many steps ahead to make comparison with
        :param n: filter threshold
        :param filter: how returns should be filtered,
                        can either be 'larger' or 'smaller'
        '''
        super(DailyMeanReversionTicker, self).__init__(start_date, end_date)
        self.t = t
        self.n = n
        self.filter = filter

    def calculate(self):
        self.data = self.get_data(values=None)
        self.calculate_all_stats()

    def calculate_all_stats(self):
        # tickers = self.data.copy().columns
        tickers = self.data.loc[:, 'ticker'].unique()
        ticker_stats = {}
        for ticker in tickers:
            ticker_stats[ticker] = self.calculate_ticker(ticker)
        self.ticker_stats = ticker_stats

    def calculate_ticker(self, ticker):
        data = self.data.loc[self.data.loc[:, 'ticker'] == ticker]
        rtns = data.sort_index().close.pct_change()
        print(ticker)
        rtns = self.get_ticker_future_returns(rtns,
                                              self.n,
                                              self.t,
                                              self.filter)
        rtn_stats = self.get_ticker_returns_stats(rtns)
        return {'return_pairs': rtns,
                'return_statistics': rtn_stats}

    def get_ticker_returns_stats(self, data):
        return {'current': self.get_stats(data, 'current_return'),
                'next': self.get_stats(data, 'next_return')}

    def get_stats(self, data, col):
        return {'mean': data.loc[:, col].mean(),
                'median': data.loc[:, col].median(),
                'std': data.loc[:, col].std(),
                'iqr': DailyMeanReversionTicker.iqr(data, col),
                'no_samples': len(data.loc[:, col])}

    @staticmethod
    def get_ticker_future_returns(data, n, t, filter_type):
        lm_data = DailyMeanReversionTicker.get_ticker_largest_price_movements(data, n, filter_type)
        rtns = []
        for idx in lm_data.index.values:
            # print(data)
            # print(data.iloc[data.index.get_loc(idx)])
            curr_idx = data.index.get_loc(idx)
            next_idx = curr_idx + t
            # print(curr_idx, next_idx, len(data))
            if next_idx < len(data):
                rtn = [idx,
                       data.iloc[curr_idx],
                       data.iloc[next_idx]]
                rtns.append(rtn)
        rtns = pd.DataFrame(data=rtns,
                            columns=['date',
                                     'current_return',
                                     'next_return'])
        return rtns

    @staticmethod
    def get_ticker_largest_price_movements(data, n, filter_type):
        filters = {'larger': data >= n,
                   'smaller': data <= n}
        data = data.pct_change()
        return data.loc[filters[filter_type]]

    @staticmethod
    def iqr(data, col):
        data = data.loc[:, col].copy()
        p75 = DailyMeanReversionTicker.get_percentile(data, 75)
        p25 = DailyMeanReversionTicker.get_percentile(data, 25)
        iqr = p75 - p25
        return iqr

    @staticmethod
    def get_percentile(data, percentile_rank):
        index = (len(data.index) - 1) * percentile_rank / 100.0
        index = int(index)
        if len(data) > 0:
            return data.loc[index]
        else:
            return 0

    def plot(self):
        pass