from incrypt.database.cdb import IcDb

import pandas as pd

class DailyCoinPriceData:
    def __init__(self, start_date, end_date,
                 coin=None, resample=None):
        db = IcDb()
        sql = ('SELECT * FROM raw.coin_daily_pricing '
               "WHERE date BETWEEN '{0!s}' AND '{1!s}' ".format(start_date,
                                                                end_date))
        if coin:
            sql += ("AND ticker = '{0!s}' ".format(coin))
        data = db.query(sql)
        if resample:
            data.index = pd.DatetimeIndex(data.index)
            data.resample(resample).last()
        else:
            self.data = data


class AllTickerData:
    def __init__(self, start_date, end_date,
                 min_len=None):
        db = IcDb()
        sql = ('SELECT DISTINCT ticker '
               'FROM raw.coin_daily_pricing '
               "WHERE date between '{0!s}' AND '{1!s}' ".format(start_date,
                                                               end_date))
        if min_len:
            sql += ('AND ticker IN '
                    '   (SELECT ticker '
                    '    FROM raw.coin_daily_pricing '
                    "    WHERE date BETWEEN '{0!s}' AND '{1!s}' "
                    '    GROUP BY ticker HAVING COUNT(*) >= {2!s}) '.format(start_date,
                                                                         end_date,
                                                                         min_len))
        data = db.query(sql)
        self.data = [x[0] for x in data.values.tolist()]