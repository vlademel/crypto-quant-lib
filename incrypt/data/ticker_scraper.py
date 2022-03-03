import datetime
import pandas as pd

from incrypt.utils import to_timestamp

class TickerScraper:
    # def __init__(self, exchange, max_retries, symbol, timeframe, since, limit):
    #     self.scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)

    def retry_fetch_ohlcv(self, exchange, max_retries, symbol, timeframe, since, limit, verbose=0):
        num_retries = 0
        while True:
            try:
                num_retries += 1
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
                if (len(ohlcv) > 0) & (verbose > 0):
                    print('Fetched', len(ohlcv), symbol, 'candles from', exchange.iso8601 (ohlcv[0][0]), 'to', exchange.iso8601 (ohlcv[-1][0]))
                return ohlcv
            except Exception:
                if num_retries > max_retries:
                    raise #Exception('Failed to fetch', timeframe, symbol, 'OHLCV in', max_retries, 'attempts')

    def scrape_ohlcv(self, exchange, max_retries, symbol, timeframe, since, limit, verbose=0):
        since = datetime.datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
        since = int(since.timestamp() * 1000)
        latest_timestamp = exchange.milliseconds()
        timeframe_duration_in_seconds = exchange.parse_timeframe(timeframe)
        timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
        timedelta = limit * timeframe_duration_in_ms
        all_ohlcv = []
        first_line = False
        while True:
            if first_line:
                fetch_since = latest_timestamp - timedelta
                ohlcv = self.retry_fetch_ohlcv(exchange, max_retries, symbol, timeframe, fetch_since, limit, verbose)
                # if we have reached the beginning of history
                # print(ohlcv)

                if len(ohlcv) < 1:
                    break
                if ohlcv[0][0] >= latest_timestamp:
                    break
                latest_timestamp = ohlcv[0][0]
                all_ohlcv = ohlcv + all_ohlcv
                # print(len(all_ohlcv), 'candles in total from', exchange.iso8601(all_ohlcv[0][0]), 'to',
                #       exchange.iso8601(all_ohlcv[-1][0]))
                # if we have reached the checkpoint
                if fetch_since < since:
                    break
            first_line = True
        data = pd.DataFrame(data=all_ohlcv, columns=['timestamp','open','high','low','close','volume'])
        data['timestamp'] = data['timestamp'].apply(to_timestamp)
        data = data.set_index('timestamp')
        return data
        # return exchange.filter_by_since_limit(all_ohlcv, since, None, key=0)
