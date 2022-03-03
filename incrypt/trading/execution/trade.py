#todo make sure each Trade object can be calculated in parralel

import datetime

from incrypt.trading.execution.trade_data import TradeData

class Trade:
    def __init__(self, exchange=None, ticker=None, amount=None,
                 side=None, type=None, price=None, params=None,
                 strategy=None):
        self.ticker = ticker
        self.amount = amount
        self.side = side
        self.type = type
        self.exchange = exchange.exchange
        self.price = price
        self.params = params
        self.strategy = strategy

    def _create_order(self, close=None):
        side = self.side
        if close:
            sides = {'buy': 'sell',
                     'sell': 'buy'}
            side = sides[side]
        self.timestamp = datetime.datetime.now()
        self.exchange.create_order(symbol=self.ticker,
                                   type=self.type,
                                   side=side,
                                   amount=self.amount)
                                   # price=self.price,
                                   # params=self.params)
        print("Order - Exchange: {0!s} | "
              "Ticker: {1!s} | Type: {2!s} | Side: {3!s} | "
              "Amount: {4!s} | Price: {5!s}".format(self.exchange.name,
                                                               self.ticker,
                                                               self.type,
                                                               self.side,
                                                               self.amount,
                                                               self.price))

    def close_trade(self):
        self._create_order(close=True)
        # self.to_csv(open=False)

    def open_trade(self):
        self._create_order()
        # self.to_csv()

    def to_table(self, close):
        trade_data = TradeData(trade=self)
        trade_data.to_table(close=close)

    def from_order_dict(self, order_dict):
        self.ticker = order_dict['symbol']
        self.amount = order_dict['amount']
        self.side = order_dict['side']
        self.type = order_dict['type']
        self.price = order_dict['price']


    def __repr__(self):
        return ("Trade - Exchange: {0!s} | " 
                "Ticker: {1!s} | Type: {2!s} | Side: {3!s} | "
                "Amount: {4!s} | Price: {5!s}".format(self.exchange.name,
                                                               self.ticker,
                                                               self.type,
                                                               self.side,
                                                               self.amount,
                                                               self.price))