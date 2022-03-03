from incrypt.database.cdb import IcDb
from incrypt.data.ticker_scraper import TickerScraper
from incrypt.database.dataloader import DataLoader
from incrypt.data.coin_price_data_base import CoinPriceDataBase

import ccxt
import pandas as pd

class CoinHfPriceData(CoinPriceDataBase):
    def __init__(self, start_date=None, limit=1000, timeframe='1m'):
        self.cdb = IcDb()
        self.ticker_scraper = TickerScraper()
        self.exchange = ccxt.binance()
        self.limit = limit
        self.timeframe = timeframe
        self.base_currency = 'usdt'
        self.key_index = 'trade_timestamp'
        self.data_loader = DataLoader(destination_schema='raw',
                                      destination_table='coin_hf_pricing',
                                      key_index=self.key_index)
        if start_date:
            self.start_date = start_date
        else:
            self.start_date = self.get_yesterday_date()

    def batch_load_data_to_sql(self, verbose=0):
        symbol_list = self.get_symbol_list()
        for symbol in symbol_list:
            data = self.get_ticker_data(symbol)
            print(data)
            if not data.empty:
                print(data)
                data.loc[:, 'ticker'] = symbol
                data.loc[:, 'exchange'] = str(self.exchange)
                data.loc[:, 'base'] = self.base_currency
                data.index.names = [self.key_index]
                data.reset_index(inplace=True)
                self.data = data
                break

                # self.to_sql()
                if verbose == 1:
                    print("Getting data for {}...".format(symbol))

    def build_delete_from_sql_query(self, ticker, exchange, start_date, end_date):
        sql = ('DELETE FROM raw.coin_hf_pricing '
               "WHERE ticker = '{ticker!s}' "
               "AND exchange = '{exchange!s}' "
               "AND trade_timestamp BETWEEN '{start_date!s}' AND '{end_date!s}' ".format(ticker=ticker,
                                                                                         exchange=exchange,
                                                                                         start_date=start_date,
                                                                                         end_date=end_date))
        return sql
