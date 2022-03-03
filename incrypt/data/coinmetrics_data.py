import pandas as pd

from coinmetrics.api_client import CoinMetricsClient

from incrypt.config import Config
from incrypt.database.cdb import IcDb
from incrypt.database.dataloader import DataLoader, DataLoadManager

class CoinMetricsData(DataLoadManager):
    def __init__(self,
                 start_date=None,
                 end_date=None):
        self.data_loader = DataLoader(destination_schema='raw',
                                      destination_table='coinmetrics_metrics',
                                      key_index='time')
        api_key = Config('coinmetrics').keys['api_key']
        self.client = CoinMetricsClient(api_key)
        self.get_start_end_dates(start_date,
                                 end_date,
                                 time=False,
                                 days=-7)

    def get_all_coins(self):
        all_assets = self.client.catalog_assets()
        asset_names = []
        for asset in all_assets:
            asset_name = asset['asset']
            asset_names.append(asset_name)
        return asset_names

    def load_data(self,
                  verbose=0):
        metrics = self.build_metrics_dict()
        all_data = []
        for metric in metrics.keys():
            data = self.client.get_asset_metrics(assets=metrics[metric]['assets'],
                                                 metrics=metric,
                                                 start_time=self.start_date,
                                                 end_time=self.end_date,
                                                 # paging_from=PagingFrom.START,
                                                 frequency=metrics[metric]['frequency'])
            all_data.append(data)
        all_metrics_data = []
        for data in all_data:
            for metric_data in data:
                metric_data = self._dict_to_df(metric_data)
                all_metrics_data.append(metric_data)
        self.data = all_metrics_data
        data = pd.concat(all_metrics_data).reset_index()
        data = data.pivot(columns='feature_name',
                           index=['asset', 'time'],
                           values='value').reset_index()
        self.data_loader.map_columns(data)
        self.data_loader.type_data(data, verbose=verbose)
        self.data = data

    def build_metrics_dict(self):
        metrics = self.client.catalog_metrics()
        metrics_dict = {}
        for metric in metrics:
            metrics_dict[metric['metric']] = metric['frequencies'][0]
        return metrics_dict

    def _dict_to_df(self, d):
        if isinstance(d, dict):
            value_key = list(d.keys())[-1]
            value = d[value_key]
            d['feature_name'] = value_key
            d['value'] = value
            d.pop(value_key)
            return pd.DataFrame(dict([(k,pd.Series(v)) for k,v in d.items() ]))
        else:
            return pd.DataFrame()

    def get_metrics(self):
        sql = ('SELECT * FROM dbo.coinmetrics_metrics')
        icdb = IcDb()
        data = icdb.query(sql).values.tolist()
        data = [i[0] for i in data]
        return data

    def to_sql(self):
        self.data_loader.to_sql(data=self.data)