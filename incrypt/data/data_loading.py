from incrypt.data.coin_info_data import CoinInfoData
from incrypt.data.coin_price_data_daily import CoinDailyPriceData
from incrypt.data.coin_price_data_hf import CoinHfPriceData
from incrypt.data.coinmetrics_data import CoinMetricsData

class DataLoading:
    def __init__(self):
        self.coin_info_data = CoinInfoData()
        self.coin_daily_price_data = CoinDailyPriceData()
        self.coin_hf_price_data = CoinHfPriceData(limit=1000)
        self.coinmetrics = CoinMetricsData()

    def load_data(self):
        to_load = [self.coin_info_data,
                   self.coin_daily_price_data,
                   self.coin_hf_price_data,
                   self.coinmetrics]
        for source in to_load:
            source.load_data()

    def to_sql(self):
        to_export = [self.coin_info_data,
                     self.coin_daily_price_data,
                     self.coin_hf_price_data,
                     self.coinmetrics]
        for source in to_export:
            source.to_sql()

    def run(self):
        self.load_data()
        self.to_sql()