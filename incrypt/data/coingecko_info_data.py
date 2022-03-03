import datetime
import pandas as pd
import time

from pycoingecko import CoinGeckoAPI

from incrypt.database.dataloader import DataLoader, DataLoadManager
from incrypt.database.cdb import IcDb

class CoinGeckoInfoData(DataLoadManager):
    def __init__(self, start_date=None, end_date=None):
        self.cg = CoinGeckoAPI()
        self.data_loader = DataLoader(destination_schema='raw',
                                      destination_table='coingecko_coin_info',
                                      key_index='date')
        self.get_start_end_dates(start_date,
                                 end_date,
                                 time=False)

    def create_date_range(self):
        start_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(self.end_date, '%Y-%m-%d')
        delta = end_date - start_date
        date_list = []
        for i in range(abs(delta.days) + 1):
            date = end_date + datetime.timedelta(days=-i)
            date = datetime.datetime.strftime(date, '%d-%m-%Y')
            date_list.append(date)
        return date_list

    def get_coin_list(self):
        sql = ('SELECT *'
               'FROM dbo.v_active_tickers')
        db = IcDb()
        data = db.query(sql)
        data = data['cg_id'].to_list()
        data = [i for i in data if i]
        return data

    def load_data(self):
        date_list = self.create_date_range()
        coin_list = self.get_coin_list()
        df_list = []
        for coin in coin_list:
            for date in date_list:
                new_data = {}
                try:
                    data = self.cg.get_coin_history_by_id(id=coin,
                                                     date=date)
                    new_data['symbol'] = data['symbol']
                    try:
                        new_data['market_cap_usd'] = data['market_data']['market_cap']['usd']
                        new_data['current_price_usd'] = data['market_data']['current_price']['usd']
                        new_data['volume_usd'] = data['market_data']['total_volume']['usd']
                    except Exception:
                        new_data['market_cap_usd'] = None
                        new_data['current_price_usd'] = None
                        new_data['volume_usd'] = None
                        print("No market data for {0!s} on {1!s}".format(coin, date))
                    try:
                        new_data['facebook_likes'] = data['community_data']['facebook_likes']
                        new_data['twitter_followers'] = data['community_data']['twitter_followers']
                        new_data['reddit_average_posts_48h'] = data['community_data']['reddit_average_posts_48h']
                        new_data['reddit_average_comments_48h'] = data['community_data']['reddit_average_comments_48h']
                        new_data['reddit_subscribers'] = data['community_data']['reddit_subscribers']
                        new_data['reddit_accounts_active_48h'] = data['community_data']['reddit_accounts_active_48h']
                    except Exception:
                        new_data['facebook_likes'] = None
                        new_data['twitter_followers'] = None
                        new_data['reddit_average_posts_48h'] = None
                        new_data['reddit_average_comments_48h'] = None
                        new_data['reddit_subscribers'] = None
                        new_data['reddit_accounts_active_48h'] = None
                        print("No community data for {0!s} on {1!s}".format(coin, date))
                    try:
                        new_data['forks'] = data['developer_data']['forks']
                        new_data['stars'] = data['developer_data']['stars']
                        new_data['subscribers'] = data['developer_data']['subscribers']
                        new_data['total_issues'] = data['developer_data']['total_issues']
                        new_data['closed_issues'] = data['developer_data']['closed_issues']
                        new_data['pull_requests_merged'] = data['developer_data']['pull_requests_merged']
                        new_data['pull_request_contributors'] = data['developer_data']['pull_request_contributors']
                        new_data['code_additions_4_weeks'] = data['developer_data']['code_additions_deletions_4_weeks']['additions']
                        new_data['code_deletions_4_weeks'] = data['developer_data']['code_additions_deletions_4_weeks']['deletions']
                    except Exception:
                        new_data['forks'] = None
                        new_data['stars'] = None
                        new_data['subscribers'] = None
                        new_data['total_issues'] = None
                        new_data['closed_issues'] = None
                        new_data['pull_requests_merged'] = None
                        new_data['pull_request_contributors'] = None
                        new_data['code_additions_4_weeks'] = None
                        new_data['code_deletions_4_weeks'] = None
                        print("No developer data for {0!s} on {1!s}".format(coin, date))
                    try:
                        new_data['alexa_rank'] = data['public_interest_stats']['alexa_rank']
                        new_data['bing_matches'] = data['public_interest_stats']['bing_matches']
                    except Exception:
                        new_data['alexa_rank'] = None
                        new_data['bing_matches'] = None
                        print("No public interest data for {0!s} on {1!s}".format(coin, date))
                    new_data['date'] = datetime.datetime.strptime(date, '%d-%m-%Y')

                    new_data = self._dict_to_df(new_data)
                    df_list.append(new_data)
                except Exception as e:
                    print(e)
                time.sleep(2)
        data = pd.concat(df_list)
        # data = data.drop_duplicates(subset=['symbol','date'])
        self.data = data

    def _dict_to_df(self, d):
        if isinstance(d, dict):
            return pd.DataFrame(dict([(k,pd.Series(v)) for k,v in d.items() ]))
        else:
            return pd.DataFrame()

    def to_sql(self):
        self.data_loader.to_sql(data=self.data)

c = CoinGeckoInfoData('2020-01-01','2021-03-26')
c.load_data()
c.to_sql()