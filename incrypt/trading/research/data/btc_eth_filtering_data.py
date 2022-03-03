from trading.research.data.daily_coin_price_data import DailyCoinPriceData

import pandas as pd
import numpy as np

class CoinFilteringData:
    def __init__(self, start_date, end_date, coin, min_len):
        self.start_date = start_date
        self.end_date = end_date
        self.coin = coin
        self.data = self.get_regression_data()
        if min_len:
            if len(self.data) < min_len:
                self.data = pd.DataFrame()

    def get_regression_data(self):
        btc = self.prepare_coin_data('btc')
        eth = self.prepare_coin_data('eth')
        coin = self.prepare_coin_data(self.coin)
        data = btc.join(eth).join(coin).dropna()
        return data

    def prepare_coin_data(self, coin_name):
        coin = DailyCoinPriceData(self.start_date,
                                 self.end_date,
                                 coin_name).data.set_index('date') \
                                .loc[:, 'close']
        coin = CoinFilteringData.get_returns(pd.DataFrame(coin))\
                                    .rename(columns={'log_r':coin_name})\
                                    .drop(['close'], axis=1)
        return coin

    @staticmethod
    def get_returns(data):
        # data.loc[:, 'pct_change'] = data.loc[:, 'close'].pct_change()
        data['log_r'] = np.log(data['close']) - np.log(data['close'].shift(1))
        return data