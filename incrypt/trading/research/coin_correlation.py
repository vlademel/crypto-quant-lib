from incrypt.database.cdb import IcDb
from incrypt.trading.research.models.btc_eth_filtering import CoinFilter
from incrypt.trading.research.models.cointegrating_pairs import CointegratedPairs
from incrypt.utils import zscore

import pandas as pd

class CoinCorrelation:
    def __init__(self, start_date=None, end_date=None):
        self.start_date = '2017-01-01'
        self.end_date = '2020-06-30'
        if start_date:
            self.start_date = start_date
        if end_date:
            self.end_date = end_date
        self.db = IcDb()

    def get_crypto_tickers(self):
        sql = ('SELECT DISTINCT ticker '
               'FROM raw.coin_daily_pricing ' 
               "WHERE date BETWEEN '{0!s}' AND '{1!s}' "
               .format(self.start_date, self.end_date))
        data = self.db.query(sql)
        data = [x[0] for x in data.values.tolist()]
        return data

    def calculate(self):
        coin_list = self.get_crypto_tickers()
        coin_list = [x for x in coin_list if x not in ['eth', 'btc']]
        pairs = {}
        for coin_1 in coin_list:
            for coin_2 in coin_list:
                if coin_1 == coin_2:
                    continue
                else:
                    pair = coin_1 + '/' + coin_2
                    pair_exists = CoinCorrelation._test_pair_exists(pair, pairs)
                    if not pair_exists:
                        self.pair = pair
                        print(pair)
                        returns = self._get_filtered_pair_returns(pair)
                        # self.returns = returns
                        if returns:
                            pairs[pair] = self._build_signal(returns)
                        else:
                            pairs[pair] = 'DATAFRAME EMPTY'
        self.data = pairs

    def _build_signal(self, pair_dict):
        coin_1 = list(pair_dict.keys())[0]
        coin_2 = list(pair_dict.keys())[1]
        if self._test_for_cointegration(pair_dict):
            coins = self._align_data(coin_1, coin_2, pair_dict)
            ratio = coins.loc[:, coin_1] / coins.loc[:, coin_2]
            z_score = zscore(ratio, 50)
            return z_score
        else:
            return 'NOT_COINTEGRATED'

    def _align_data(self, coin_1, coin_2, pair_dict):
        coin_1 = pd.DataFrame(pair_dict[coin_1])
        coin_2 = pd.DataFrame(pair_dict[coin_2])
        data = coin_1.join(coin_2, how='outer')
        data.dropna(inplace=True)
        return data

    def _get_filtered_pair_returns(self, pair):
        coin_1 = pair.split('/')[0]
        coin_2 = pair.split('/')[1]
        coin_dict = {coin_1: None,
                     coin_2: None}
        for coin in coin_dict.keys():
            cf = CoinFilter(start_date=self.start_date,
                           end_date=self.end_date,
                           coin=coin)
            filtered_ret = cf.nonlinear_regression_filter()
            coin_dict[coin] = filtered_ret
        if self._returns_not_exist(coin_dict):
            return None
        else:
            return coin_dict

    def _returns_not_exist(self, coin_dict):
        for coin in coin_dict.keys():
            if isinstance(coin_dict[coin], pd.Series):
                continue
            else:
                return True

    def _test_for_cointegration(self, pair_dict):
        coin_1 = list(pair_dict.keys())[0]
        coin_2 = list(pair_dict.keys())[1]
        y0 = pair_dict[coin_1]
        y1 = pair_dict[coin_2]
        coint = CointegratedPairs(y0, y1).cointegrated
        return coint

    @staticmethod
    def _test_pair_exists(pair, pairs):
        pair_split = pair.split('/')
        pair_reversed = pair_split[1] + '/' + pair_split[0]
        if pair in pairs:
            return True
        elif pair_reversed in pairs:
            return True
        else:
            return False