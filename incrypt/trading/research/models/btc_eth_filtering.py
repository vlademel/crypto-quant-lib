import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
import pandas as pd

from trading.research.data.btc_eth_filtering_data import CoinFilteringData

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LassoCV
from sklearn.pipeline import make_pipeline
from sklearn import linear_model

import numpy as np

class CoinFilter:

    MIN_DATA_LEN = 50

    def __init__(self, start_date, end_date, coin):
        self.start_date = start_date
        self.end_date = end_date
        self.coin = coin
        self.data = CoinFilteringData(start_date,
                                      end_date,
                                      coin,
                                      self.MIN_DATA_LEN).data

    @staticmethod
    def vif(X):
        return pd.Series([variance_inflation_factor(X.values, i)
                                for i in range(X.shape[1])],
                                index=X.columns)

    def linear_regression_filter(self):
        data = self.data.copy()
        X = add_constant(data)
        vif = CoinFilter.vif(X)
        if vif['btc'] <= 5:
            lin_1 = sm.OLS(X[self.coin], X.drop(self.coin, axis=1))
            results_1 = lin_1.fit()
            filtered = results_1.resid
        else:
            lin_1 = sm.OLS(X[self.coin], X.loc[:, 'eth'])
            results_1 = lin_1.fit()
            errors_1 = results_1.resid
            lin_2 = sm.OLS(errors_1, X.loc[:, 'btc'])
            results_2 = lin_2.fit()
            filtered = results_2.resid
        return filtered

    def nonlinear_regression_filter(self):
        if not self.data.empty:
            # print(self.data)
            degree = self.get_optimal_poly_config()
            data = self.data.copy().dropna()
            vif = CoinFilter.vif(add_constant(data))
            data = data.values
            if vif['btc'] <= 5:
                # X = data.drop(self.coin, axis=1)
                X = data[:, :2]
                X = self.add_polynomial_features(X, degree)
                # y = data.loc[:, self.coin].values
                y = data[:, 2]

                reg_1 = self.fit_lasso_model(X=X, y=y)
                y_hat = reg_1.predict(X)
                filtered = y - y_hat
            else:
                # X = data.loc[:, 'eth']
                X = data[:, 1]
                X = self.add_polynomial_features(X, degree)
                # y = data.loc[:, self.coin].values
                y = data[:, 2]

                reg_1 = self.fit_lasso_model(X=X, y=y)
                y_hat = reg_1.predict(X)
                y = data[:, 2]
                errors_1 = y - y_hat

                # X = data.loc[:, 'btc']
                X = data[:, 0]
                X = self.add_polynomial_features(X, degree)
                y = errors_1

                reg_2 = self.fit_lasso_model(X=X, y=y)
                y_hat = reg_2.predict(X)
                # y = X.loc[:, self.coin].values
                y = data[:, 2]
                filtered = y - y_hat
            return filtered
        else:
            return None

    def add_polynomial_features(self, X, degree):
        if len(X.shape) < 2:
            X = X.reshape(-1, 1)
        poly = PolynomialFeatures(degree)
        # feature_names = X.columns
        X = poly.fit_transform(X=X)
        # new_feature_names = poly.get_feature_names(feature_names)
        # print(new_feature_names)
        return X

    def fit_lasso_model(self, X, y):
        lasso_iter = 10000
        lasso_alpha = 0.00001

        if isinstance(y, pd.DataFrame):
            y = y.values
        model = linear_model.Lasso(alpha=lasso_alpha, max_iter=lasso_iter)
        model.fit(X, y)
        return model

    def fit_cv_lasso_model(self, X, y, degree):
        lasso_eps = 0.0001
        lasso_nalpha = 20
        lasso_iter = 10000
        model = make_pipeline(PolynomialFeatures(degree, interaction_only=False),
                              LassoCV(eps=lasso_eps, n_alphas=lasso_nalpha,
                                      max_iter=lasso_iter, normalize=True, cv=5))
        model.fit(X, y)
        return model

    def get_optimal_poly_config(self):
        df = self.data.copy()
        X = df.drop(self.coin, axis=1)
        Y = df.loc[:, self.coin]

        degree_min = 1
        degree_max = 8

        test_set_fraction = 0.7

        X_train, X_test, \
        y_train, y_test = train_test_split(X, Y, test_size=test_set_fraction)

        # degree_perf = {}
        min_rmse = None
        for degree in range(degree_min, degree_max + 1):
            model = self.fit_cv_lasso_model(X_train, y_train, degree)
            test_pred = np.array(model.predict(X_test))
            RMSE = np.sqrt(np.sum(np.square(test_pred - y_test)))
            # test_score = model.score(X_test, y_test)
            # degree_perf[degree] = {'rmse': RMSE,
            #                        'test_score': test_score}
            if not min_rmse:
                optimal_degree = degree
            elif RMSE < min_rmse:
                min_rmse = RMSE
                optimal_degree = degree
        return optimal_degree

# c = CoinFilter('2019-06-01','2020-12-31','nano')
# # filtered = c.nonlinear_regression_filter()
# data_1 = c.data.copy()
# X = data_1.drop('nano', axis=1)
# # X = self.add_polynomial_features(X, degree)
# y = data_1.loc[:, 'nano']
# poly = PolynomialFeatures(2)
# X = poly.fit_transform(X=X)
#
# lasso_iter = 10000
# lasso_alpha = 0.00001
# reg_1 = linear_model.Lasso(alpha=lasso_alpha, max_iter=lasso_iter)
# reg_1.fit(X, y)
# y_hat = reg_1.predict(X)
# filtered = y - y_hat
#
#
# c = CoinFilter('2019-06-01','2020-12-31','xrp')
# # filtered = c.nonlinear_regression_filter()
# data_2 = c.data.copy()
# X = data_2.drop('xrp', axis=1)
# # X = self.add_polynomial_features(X, degree)
# y = data_2.loc[:, 'xrp']
# poly = PolynomialFeatures(2)
# X = poly.fit_transform(X=X)
#
# lasso_iter = 10000
# lasso_alpha = 0.00001
# reg_2 = linear_model.Lasso(alpha=lasso_alpha, max_iter=lasso_iter)
# reg_2.fit(X, y)
# y_hat = reg_1.predict(X)
# filtered_2 = y - y_hat
#
#
#
# ratio = filtered / filtered_2
# from incrypt.utils import zscore
# score = zscore(ratio, 50)
#
# ratio_2 = data_1['nano'] / data_2['xrp']
# score_2 = zscore(ratio_2, 50)
#
# import matplotlib.pyplot as plt
#
# plt.plot(score_2)
# plt.plot(score)