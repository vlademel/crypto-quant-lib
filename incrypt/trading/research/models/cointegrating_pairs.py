import statsmodels.tsa.stattools as ts

class CointegratedPairs:

    def __init__(self, y0, y1, c_val=0.05):
        self.y0 = y0
        self.y1 = y1
        self.c_val = c_val
        self.cointegrated = self._test_cointegration()

    def _test_cointegration(self):
        coint = ts.coint(self.y0,
                         self.y1)
        p_val = coint[1]
        if p_val < self.c_val:
            return True
        else:
            return False