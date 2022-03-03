from incrypt.database.cdb import IcDb

import pandas as pd

class SimpleReversalData:
    def __init__(self, start_date, end_date,
                 coin=None, resample=None):
        db = IcDb()
        sql = ('SELECT * FROM dbo.v_simple_reversal_data '
               "WHERE date BETWEEN '{0!s}' AND '{1!s}' "
               'AND market_cap_usd IS NOT NULL '
               'AND market_cap_usd != 0 '
               'AND ticker NOT IN '
               "    ('one', 'key', 'hot', 'stx', 'ftt', 'mft', 'tct', 'hive', 'pnt', 'grt') ".format(start_date,
                                                end_date))
        if coin:
            sql += ("AND ticker = '{0!s}' ".format(coin))
        data = db.query(sql)
        if resample:
            data.index = pd.DatetimeIndex(data.index)
            data.resample(resample).last()
        else:
            self.data = data

    # @staticmethod
    # def create_market_cap_ranking(data):
    #     # create ranking by market cap - maybe include percentile?
