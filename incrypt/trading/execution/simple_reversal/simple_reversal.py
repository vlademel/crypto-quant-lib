from incrypt.trading.execution.exchange_login import ExchangeApi
from incrypt.trading.execution.position_sizer import PositionSizer
from incrypt.trading.execution.trade import Trade
from incrypt.trading.execution.trade_observer import TradeObserver
from incrypt.trading.execution.strategy import BaseStrategy
from incrypt.data.ticker_scraper import TickerScraper

import datetime
import pandas as pd
import logging

class SimpleReversal(BaseStrategy):
    def __init__(self, threshold):
        self.threshold = threshold
        self.name = 'simple_reversal'
        self.exchange = ExchangeApi('binance').exchange
        self._initialise_open_positions()

    def get_data(self):
        yesterday = (datetime.date.today() - datetime.timedelta(days=1))\
                        .strftime('%Y-%m-%d') + ' 00:00:00'
        tickers = list(self.exchange.exchange.fetch_tickers().keys())
        tickers = [ticker for ticker in tickers if ticker.split('/')[1] == 'USDT']
        data_list = []
        for ticker in tickers:
            tmp = TickerScraper().scrape_ohlcv(exchange=self.exchange.exchange,
                                                timeframe='1d',
                                                symbol=ticker,
                                                max_retries=3,
                                                since=yesterday,
                                                limit=2)
            if not tmp.empty:
                tmp.loc[:, 'ticker'] = ticker
                data_list.append(tmp)
        data = pd.concat(data_list)
        self.data = data.pivot_table(index='timestamp',
                                     columns='ticker',
                                     values='close')\
                                    .pct_change().dropna()

    def get_largest_fallers(self):
        tickers = [i.upper() for i in self.data.columns]
        values = self.data.values.tolist()[0]
        data = {ticker: value for (ticker, value) in
                zip(tickers, values) if value < self.threshold}
        data = dict(sorted(data.items(), key=lambda item: item[1]))
        self.data = data
        print(data)

    def open_positions(self):
        self.trades = []
        for ticker in self.data.keys():
            pos = PositionSizer(exchange=self.exchange,
                                position_pct=1.0,
                                ticker=ticker)
            amount = pos.crypto_size
            if amount > 0:
                trade = Trade(exchange=self.exchange,
                              ticker=ticker,
                              amount=amount,
                              side='buy',
                              type='market')
                print("Creating trade object: {}".format(trade))
                self.trades.append(trade)

        for trade in self.trades:
            print("Opening trade {}...".format(trade))
            trade.open_trade()

        trd_obs = TradeObserver(self.trades)
        trd_obs.check_trades_status()

        for trade in self.trades:
            # trade.to_csv()
            trade.to_table()

    def close_positions(self):
        for trade in self.trades:
            print("Closing trade {}...".format(trade))
            trade.close_trade()

        trd_obs = TradeObserver(self.trades)
        trd_obs.check_trades_status()

        for trade in self.trades:
            # trade.to_csv()
            trade.to_table(close=True)

        self.trades = []

    def trade(self):
        self.get_data()
        self.get_largest_fallers()
        if len(self.trades) > 0:
            self.close_positions()
        self.open_positions()

    def run(self):
        while True:
            now = datetime.datetime.today()
            hour = now.hour
            minute = now.minute
            second = now.second
            if hour == 23 and minute == 58 \
                and second == 58:
                self.exchange = ExchangeApi('binance')
                self.trade()
