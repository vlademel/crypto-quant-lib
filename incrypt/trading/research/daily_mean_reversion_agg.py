from incrypt.trading.research.daily_mean_reversion_base import DailyMeanReversionBase

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class DailyMeanReversionAgg(DailyMeanReversionBase):
    def calculate(self):
        data = self.get_data()
        biggest_fallers = DailyMeanReversionAgg.get_biggest_fallers(data, 180, 8)
        lowest_returns = DailyMeanReversionAgg.calculate_returns(biggest_fallers, 8)
        self.returns, self.deltas = lowest_returns, biggest_fallers
        self.plot_returns(1)

    def plot_returns(self, n):
        to_plot = ['ret_t_' + str(i) for i in range(1, n+1)]
        data = self.returns.loc[:, to_plot]
        for col in to_plot:
            plt.plot(data.loc[:, col].cumsum(), label = col)
        plt.legend()
        plt.show()

    @staticmethod
    def get_close_for_n_periods_ahead(data, n, current_idx, ticker, date):
        data = data.loc[:, ticker]
        n_periods = {'ticker': ticker,
                     'date':date}
        current_idx = data.index.get_loc(current_idx)
        for i in range(0, n + 1):
            next_idx = current_idx + i
            if next_idx < len(data):
                n_periods['t_' + str(i)] = [data.iloc[next_idx]]
            else:
                n_periods['t_' + str(i)] = np.nan
        return pd.DataFrame(n_periods)

    @staticmethod
    def calculate_returns(data, n):
        cols = ['t_' + str(i) for i in range(1, n + 1)]
        for col in cols:
            data.loc[:, 'ret_' + col] = (data.loc[:, col] - data.loc[:, 't_0'])  / data.loc[:, 't_0']
        data = data.groupby('date').sum()
        return data

    @staticmethod
    def get_n_smallest_tickers(data, n, idx, filter=None):
        data = data.loc[idx, :].T.sort_values()
        tickers = data.iloc[:n,]
        tickers = tickers.loc[tickers < -.1]
        return tickers.index.values

    @staticmethod
    def get_biggest_fallers(data, no_of_tickers, periods_ahead, period=None):
        if period:
            data.index = pd.to_datetime(data.index)
            data_resampled = data.resample(period).last()
            data_resampled.index = data_resampled.index.date
            data.index = data.index.date
            returns = data_resampled.pct_change()
        else:
            returns = data.pct_change()
        lowest_returns = []
        for idx in returns.index.values:
            tickers = DailyMeanReversionAgg.get_n_smallest_tickers(returns, no_of_tickers, idx)
            for ticker in tickers:
                if returns.index.get_loc(idx) == 0:
                    continue
                elif returns.index.get_loc(idx) < len(data) - 1:
                    prices = DailyMeanReversionAgg.get_close_for_n_periods_ahead(data, periods_ahead, idx, ticker, idx)
                    lowest_returns.append(prices)

        lowest_returns = pd.concat(lowest_returns)
        return lowest_returns
