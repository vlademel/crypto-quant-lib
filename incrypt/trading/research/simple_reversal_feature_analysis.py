from incrypt.trading.research.data.simple_reversal_data import SimpleReversalData


class SimpleReversalFeatAnalysis:
    def __init__(self, start_date, end_date):
        self.data = SimpleReversalData(start_date, end_date).data

    def forward_fill(self):
        data = self.data.copy()
        self.data = data.sort_values('date', ascending=False) \
                        .groupby('ticker', sort=False).ffill()

    def pivot(self):
        data = self.data.copy()
        self.data = data.pivot_table(index='date', columns='symbol')

