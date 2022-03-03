from pycoingecko import CoinGeckoAPI
import pandas as pd
import numpy as np
import time

from incrypt.database.dataloader import DataLoader
from incrypt.utils import string_to_datetime

class CoinInfoData:
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.data_loader = DataLoader(destination_schema='raw',
                                      destination_table='coin_market_detail',
                                      key_index='unique_key')

    @staticmethod
    def create_unique_key(row):
        last_updated = string_to_datetime(row['last_updated'])
        unix_secs = time.mktime(last_updated.timetuple())
        key = row['symbol'] + str(unix_secs)
        return key

    @staticmethod
    def remove_duplicates(data):
        data.drop_duplicates(subset='unique_key', inplace=True)
        return data

    def load_data(self):
        market_data = self.get_coin_market_data()
        market_data.drop(['image','roi']
                         , axis=1,
                         inplace=True)
        market_data = market_data.dropna(subset=['last_updated'])
        market_data.loc[:, 'unique_key'] = market_data.apply(CoinInfoData.create_unique_key, axis=1)
        market_data = CoinInfoData.remove_duplicates(market_data)
        self.data = market_data

    def get_coin_market_data(self, verbose=0):
        df_list = []
        for i in range(1, 80):
            if verbose==1:
                print("Getting page {0!s}...".format(i))
            data = self.cg.get_coins_markets('usd', per_page=100, page=i)
            df = self.to_dataframe(data)
            df_list.append(df)
            time.sleep(1)
        return pd.concat(df_list)

    def to_dataframe(self, market_data):
        return pd.DataFrame(market_data)

    def to_sql(self):
        self.data_loader.to_sql(data=self.data)