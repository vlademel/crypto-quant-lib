from incrypt.database.cdb import IcDb
from incrypt.data.ticker_scraper import TickerScraper
from incrypt.database.dataloader import DataLoader
from incrypt.data.coin_price_data_base import CoinPriceDataBase

import ccxt

class CoinDailyPriceData(CoinPriceDataBase):
    def __init__(self, start_date=None, limit=1, timeframe='1d'):
        self.cdb = IcDb()
        self.ticker_scraper = TickerScraper()
        self.exchange = ccxt.binance()
        self.limit = limit
        self.timeframe = timeframe
        self.base_currency = 'usdt'
        self.key_index = 'date'
        self.data_loader = DataLoader(destination_schema='raw',
                                      destination_table='coin_daily_pricing',
                                      key_index=self.key_index)
        if start_date:
            self.start_date = start_date
        else:
            self.start_date = self.get_yesterday_date()

    def build_delete_from_sql_query(self, ticker, exchange, start_date, end_date):
        sql = ('DELETE FROM raw.coin_daily_pricing '
               "WHERE ticker = '{ticker!s}' "
               "AND exchange = '{exchange!s}' "
               "AND date BETWEEN '{start_date!s}' AND '{end_date!s}' ".format(ticker=ticker,
                                                                              exchange=exchange,
                                                                              start_date=start_date,
                                                                              end_date=end_date))
        return sql
