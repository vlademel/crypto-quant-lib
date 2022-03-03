from incrypt.database.ddb import DDb
from incrypt.trading.execution.trade import Trade

import boto3

class BaseStrategy:
    def _get_open_positions(self):
        open_trades_table_name = 'open_trades_' + self.name
        dynamodb_client = boto3.client('dynamodb')
        tables_list = dynamodb_client.list_tables()['TableNames']
        if open_trades_table_name in tables_list:
            open_trades = DDb(open_trades_table_name)
            open_trades = open_trades.scan()
            if len(open_trades) > 0:
                return True, open_trades
        else:
            return False, None

    def _initialise_open_positions(self):
        self.trades = []
        is_open, open_trades = self._get_open_positions()
        if is_open:
            for trade in open_trades:
                trade_obj = Trade(exchange=self.exchange.exchange)
                trade_obj.from_order_dict(order_dict=trade)
                self.trades.append(trade_obj)