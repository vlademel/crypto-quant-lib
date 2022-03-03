from incrypt.trading.execution.exchange_login import ExchangeApi

import time

class TradeObserver:
    def __init__(self, trades):
        self.trades = trades
        self.exchange = ExchangeApi('binance').exchange

    def check_trades_status(self):
        for trade in self.trades:
            is_open = True
            while is_open:
                order_data = self.exchange.fetch_order(id=trade.id,
                                                       symbol=trade.symbol)
                if order_data['status'] == 'closed':
                    is_open = False
                time.sleep(0.1)
