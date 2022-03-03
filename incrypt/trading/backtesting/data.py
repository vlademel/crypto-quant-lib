from trading.research.data.daily_coin_price_data import DailyCoinPriceData
from trading.research.data.daily_coin_price_data import AllTickerData

import backtrader as bt
import pandas as pd

class DailyCoinBacktraderData:
    def __init__(self, start_date, end_date,
                 coin=None, min_len=None):
        if not coin:
            tickers = AllTickerData(start_date, end_date).data
            df_list = []
            for ticker in tickers:
                data = DailyCoinPriceData(start_date, end_date, ticker).data
                if min_len:
                    if len(data) >= min_len:
                        data = self.process_df(data)
                        df_list.append(data)
                else:
                    if not data.empty:
                        data = self.process_df(data)
                        df_list.append(data)
            self.data = df_list
        else:
            data = DailyCoinPriceData(start_date, end_date, coin).data
            data = self.process_df(data)
            self.data = data

    def process_df(self, df):
        df = df.drop(['ticker', 'exchange'], axis=1)
        df = df.rename(columns={'date': 'datetime'})
        df = df.set_index('datetime')
        df.loc[:, 'openinterest'] = 0
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
        df = bt.feeds.PandasData(dataname=df)
        return df