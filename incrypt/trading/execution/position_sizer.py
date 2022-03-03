class PositionSizer:
    def __init__(self, exchange, position_pct,
                 ticker, price=None):
        self.exchange = exchange.exchange
        self.position_pct = position_pct
        self.ticker = ticker
        self.price = price
        self._get_position_size()

    def _get_account_balance(self):
        balance = self.exchange.fetch_balance()['total']['USDT']
        self.balance = self._account_balance_check(balance)

    def _get_position_size(self):
        self._get_account_balance()
        self._get_fiat_size()
        self._get_crypto_size()

    def _get_current_price(self):
        self.last_price = self.exchange.fetch_ticker(self.ticker)['last']

    def _get_fiat_size(self):
        self.fiat_size = self.balance * self.position_pct

    def _get_crypto_size(self):
        self._get_current_price()
        if self.fiat_size >= 10:
            self.crypto_size = self.fiat_size / self.last_price
        else:
            self.crypto_size = 0

    def _account_balance_check(self, balance):
        if balance <= 10:
            print("Not enough USDT in account to meet minimum size requirements")
            return 0
        else:
            return balance
#
# from incrypt.trading.execution.exchange_login import ExchangeApi
#
# exchange = ExchangeApi('binance')
# pos = PositionSizer(exchange=exchange,
#                     position_pct=1.0,
#                     ticker='ADA/USDT')