import ccxt

from incrypt.config import Config

class ExchangeApi:
    def __init__(self, exchange_name):
        config = Config(exchange_name.upper())
        self.api_key = config.keys['api_key']
        self.secret_key = config.keys['secret_key']
        self.exchange_name = exchange_name
        self.login()

    def login(self):
        exchange_class = getattr(ccxt, self.exchange_name)
        exchange = exchange_class({
                    'apiKey': self.api_key,
                    'secret': self.secret_key,
                    'timeout': 30000,
                    'enableRateLimit': True, })
        self.exchange = exchange