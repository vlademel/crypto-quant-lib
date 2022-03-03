from incrypt.database.cdb import IcDb
from trading.research.data.daily_coin_price_data import DailyCoinPriceData
from incrypt.trading.research.data.simple_reversal_data import SimpleReversalData


class DailyMeanReversionBase:
    def __init__(self, start_date=None, end_date=None):
        self.start_date = '2017-01-01'
        self.end_date = '2021-02-28'
        if start_date:
            self.start_date = start_date
        if end_date:
            self.end_date = end_date
        self.db = IcDb()

    def get_crypto_tickers(self):
        sql = ('SELECT DISTINCT ticker '
               'FROM raw.coin_daily_pricing ')
        data = self.db.query(sql)
        data = [x[0] for x in data.values.tolist()]
        return data

    def get_data(self, values='close'):
        data = SimpleReversalData(self.start_date, self.end_date).data
        if values:
            return data.pivot_table(index='date', columns='ticker', values=values)
        else:
            data = data.set_index('date')
            return data

