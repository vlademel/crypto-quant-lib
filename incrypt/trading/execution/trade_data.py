import pandas as pd
import boto3
import re

from incrypt.utils import flatten
from incrypt.database.ddb import DDb

from datetime import datetime

class TradeData:
    def __init__(self, trade):
        self.exchange = trade.exchange
        self.trade = trade
        self.ticker = trade.ticker
        self.timestamp = trade.timestamp
        self.open_trades_table_name = 'open_trades_' + trade.strategy.name

    def get_order_info_by_timestamp(self):
        order_info = self.exchange.fetch_my_trades(symbol=self.ticker,
                                                   since=int(self.timestamp.timestamp()))
        order_info = TradeData.parse_order_info(order_info)
        self.order_info = order_info
        self.order_id = order_info['info_orderId']
        self.symbol = order_info['symbol']

    def get_order_info_by_id(self, order_id=None):
        if not order_id:
            order_id = self.order_id
        self.order_info = self.exchange.fetch_order(id=order_id,
                                                    symbol=self.symbol)

    @staticmethod
    def parse_order_info(order_info):
        order_info = flatten(order_info)
        # order_info = TradeData.order_info_to_dataframe(order_info)
        return order_info

    @staticmethod
    def order_info_to_dataframe(order_info):
        for key in order_info.keys():
            order_info[key] = [order_info[key]]
        order_info = pd.DataFrame(order_info)
        return order_info

    def to_csv(self, open=True):
        if open:
            trade_type = 'OPEN_'
        else:
            trade_type = 'CLOSE_'
        csv_name = trade_type + str(self.order_info['info_orderId']) \
                    + str(self.order_info['datetime']) + '.csv'
        self.order_info.to_csv(csv_name)

    def to_table(self, close):
        self.get_order_info_by_timestamp()
        if close:
            self.order_info['order_context'] = 'close'
            self.order_info['strategy'] = self.trade.strategy.name
            self.close_trade_to_table()
        else:
            self.order_info['order_context'] = 'open'
            self.order_info['strategy'] = self.trade.strategy.name
            self.open_trade_to_table()

    def open_trade_to_table(self):
        dynamodb_client = boto3.client('dynamodb')
        tables_list = dynamodb_client.list_tables()['TableNames']
        if not self.open_trades_table_name in tables_list:
            self.create_open_trades_table()
        open_trades = DDb(self.open_trades_table_name)
        open_trades.insert_to_table(self.order_info)
        trades = DDb('trades')
        trades.insert_to_table(self.order_info)

    def close_trade_to_table(self):
        dynamodb_client = boto3.client('dynamodb')
        tables_list = dynamodb_client.list_tables()['TableNames']
        if self.open_trades_table_name in tables_list:
            self.delete_open_trades_table()
        trades = DDb('trades')
        trades.insert_to_table(self.order_info)

    def delete_open_trades_table(self):
        open_trades = DDb(self.open_trades_table_name)
        open_trades.delete_table()

    def create_open_trades_table(self):
        table_name = self.open_trades_table_name
        partition_key = {'name': 'id',
                         'key_type': 'HASH',
                         'attribute_type': 'N'}
        sort_key = {'name': 'datetime',
                    'key_type': 'RANGE',
                    'attribute_type': 'S'}
        DDb.create_table(table_name=table_name,
                         partition_key=partition_key,
                         sort_key=sort_key)
