import datetime
import numpy as np
import pandas as pd
import names

from utils.market_data import MarketData


class RandomPortfolio:
    market_data = None
    raw_data = None
    profiles = ['PRUDENT', 'EQUILIBRE', 'DYNAMIQUE', 'ABS RETURN']
    types = ['MANDAT', 'FCP', 'ASV']
    color_dic = {
            'PRUDENT': 'rgb(255, 255, 102)',  # pale yellow
            'EQUILIBRE': 'rgb(51, 51, 255)',  # profound blue
            'DYNAMIQUE': 'rgb(255, 0, 0)',  # red
            'ABS RETURN': 'rgb(0, 153, 51)'
        }

    def __init__(self, id, min_securities=10, max_securities=50):

        self.size = np.random.randint(min_securities, max_securities)
        self._tickers = None
        self._weights = None
        self.id = id
        self.fund_manager = names.get_full_name()
        self.client = names.get_full_name()
        self.creation_date = datetime.date(year=np.random.randint(2002, 2017), month=np.random.randint(1, 12),
                                           day=np.random.randint(1, 28))
        self.type = np.random.choice(RandomPortfolio.types)

        self._start = None
        self._end = None

    @classmethod
    def set_market_data(cls, market_data: MarketData):
        cls.market_data = market_data
        cls.raw_data = market_data.data

    @property
    def tickers(self):
        assert isinstance(RandomPortfolio.market_data, MarketData), \
            "Market data not set. Use set_market_data method first."

        if self._tickers is None:
            self._tickers = np.random.choice(self.market_data.securities, self.size)
        return self._tickers

    @tickers.setter
    def tickers(self, array):

        assert len(array) == self.size, 'array size must be equal to ptf size.'
        for ticker in array:
            assert ticker in self.market_data.securities, "{} not in available securities".format(ticker)

        self._tickers = array

    @property
    def weights(self):
        if self._weights is None:
            w = np.random.randint(1, 10, size=self.size)
            w = w/np.sum(w)
            self._weights = w
        return self._weights

    @weights.setter
    def weights(self, array: np.array):

        assert len(array) == self.size, 'array size must be equal to ptf size.'
        assert abs(array.sum() - 1) < 0.0001, 'array sum must be almost equal to 1.'
        self._weights = array

    def securities_close(self, start, end):
        closes = RandomPortfolio.raw_data.loc[start:end:, self.tickers]
        closes.columns = self.tickers

        return closes

    def securities_returns(self, start, end, resample=None):

        assert isinstance(RandomPortfolio.market_data, MarketData), \
            "Market data not set. Use set_market_data method first."

        closes = self.securities_close(start, end)
        # TO DO: check by date
        if resample is not None:

            perfs = closes.resample(resample).agg(lambda x: x[-1]/x[1] - 1)
        else:
            perfs = (closes/closes.shift(1) - 1)

        return perfs

    def ptf_histo_value(self, start: str, end: str):
        closes = self.securities_close(start, end)
        return (closes / closes.iloc[0]).dot(self.weights)

    def ptf_returns(self, start: str, end: str):
        return self.ptf_histo_value(start, end).pct_change()

    def variance(self, start: str, end: str):
        var = np.dot(self.weights.T, np.dot(self.securities_returns(start, end).cov()*252, self.weights))
        return var

    def perf(self, start: str, end: str, **kwargs):

        histo_val = self.ptf_histo_value(start, end)

        return histo_val[-1] / histo_val[0] - 1

    def indices_beta(self, start: str, end: str):
        indices_returns = RandomPortfolio.market_data.indices_returns[start:end]

        df = pd.concat([self.ptf_returns(start, end), indices_returns], axis=1, join='inner')

        return (df.cov()[0] / df.var())[1:]


