from pycoingecko import CoinGeckoAPI
import pandas as pd
import time

from incrypt.database.dataloader import DataLoader, DataLoadManager

class CoinGeckoTickerData(DataLoadManager):
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.data_loader = DataLoader(destination_schema='raw',
                                      destination_table='coingecko_tickers',
                                      key_index='symbol')

    def load_data(self):
        data_list = []
        for i in range(1, 90):
            all_data = self.cg.get_coins_markets('usd', per_page=100, page=i)
            for data in all_data:
                for dat in data:
                    tmp = pd.DataFrame()
                    tmp['id'] = [dat['id']]
                    tmp['symbol'] = [dat['symbol']]
                    tmp['name'] = [dat['name']]
                data_list.append(tmp)
            time.sleep(1)
        data = pd.concat(data_list).reset_index()
        data.drop_duplicates(inplace=True)
        self.data = data_list

    def to_sql(self):
        self.data_loader.to_sql(self.data)

c = CoinGeckoTickerData()
c.load_data()