import pandas as pd
import datetime

from incrypt.trading.execution.exchange_login import ExchangeApi

class CoinPriceDataBase:
    def get_symbol_list(self):
        exchange = ExchangeApi('binance')
        tickers = list(exchange.exchange.fetch_tickers().keys())
        tickers = [ticker for ticker in tickers if ticker.split('/')[1] == 'USDT']
        # sql = ('SELECT DISTINCT(symbol) '
        #        'FROM raw.coin_market_detail ')
        # data = self.cdb.query(sql)
        # data = data.loc[:, 'symbol'].values.tolist()
        return tickers

    def get_yesterday_date(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        date = yesterday.strftime('%Y-%m-%d') + ' 00:00:00'
        return date

    def build_ticker(self, symbol):
        #todo make this more intelligent - have a table with base ticker & exchange pairings
        exch_name = self.exchange.name
        if exch_name == 'Binance':
            ticker = symbol.upper() + '/' + self.base_currency.upper()
            return ticker

    def get_ticker_data(self, symbol):
        empty_df = pd.DataFrame(columns=['open','high','low','close',
                                         'volume','ticker','exchange'])
        if symbol:
            # ticker = self.build_ticker(symbol)
            try:
                return self.ticker_scraper.scrape_ohlcv(exchange=self.exchange,
                                                        max_retries=3,
                                                        symbol=symbol,
                                                        timeframe=self.timeframe,
                                                        since=self.start_date,
                                                        limit=self.limit)
            except Exception as e:
                print(e)
                return empty_df
        else:
            return empty_df

    def load_data(self, verbose=0):
        symbol_list = self.get_symbol_list()
        df_list = []
        for symbol in symbol_list:
            data = self.get_ticker_data(symbol)
            if not data.empty:
                data.loc[:, 'ticker'] = symbol.split('/')[0].lower()
                data.loc[:, 'exchange'] = str(self.exchange)
                df_list.append(data)
                if verbose == 1:
                    print("Getting data for {}...".format(symbol))
        self.data = df_list
        df_list = [x for x in df_list if x is not None]
        df = pd.concat(df_list)
        df.loc[:, 'base'] = self.base_currency
        df.index.names = [self.key_index]
        df.reset_index(inplace=True)
        self.data = df

    def delete_from_sql(self, data):
        sql_list = []
        tickers = data.loc[:, 'ticker'].unique()
        exchanges = data.loc[:, 'exchange'].unique()
        for ticker in tickers:
            for exchange in exchanges:
                tmp = data.loc[(data.loc[:,'ticker']==ticker) & (data.loc[:,'exchange']==exchange)]
                start_date = min(tmp.loc[:, self.key_index])
                end_date = max(tmp.loc[:, self.key_index])
                sql = self.build_delete_from_sql_query(ticker, exchange, start_date, end_date)
                sql_list.append(sql)
        for sql in sql_list:
            self.data_loader.db.run_query(sql)

    def to_sql(self):
        self.delete_from_sql(self.data)
        self.data_loader.insert_to_sql(data=self.data)
