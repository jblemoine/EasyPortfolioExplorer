import datetime
import numpy as np
import pandas as pd
from functools import lru_cache

from EasyPortfolioExplorer import names
from EasyPortfolioExplorer.app.utils.market_data import MarketData


class RandomPortfolio:
    """
    A market porfolio composed of securities. Securities are randomly picked among market data universe.

    """
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
        """

        :param id: str
            Identification number
        :param min_securities: str, default 10
            Lower bound for number of securities
        :param max_securities: str, default 50
            Upper bound for number of securities
        """

        self.size = np.random.randint(min_securities, max_securities)
        self._tickers = None
        self._weights = None
        self.id = id
        self.fund_manager = names.get_full_name()
        self.client = names.get_full_name()
        self.creation_date = datetime.date(year=np.random.randint(2002, 2017), month=np.random.randint(1, 12),
                                           day=np.random.randint(1, 28))
        self.type = np.random.choice(RandomPortfolio.types)

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

    @lru_cache(maxsize=1024)
    def securities_close(self, start, end):

        closes = RandomPortfolio.raw_data[start:end][self.tickers]
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
        arr = (closes / closes.iloc[0]).dot(self.weights)
        return arr

    def ptf_returns(self, start: str, end: str):
        return self.ptf_histo_value(start, end).pct_change()

    def variance(self, start: str, end: str):
        """

        Compute the annualised variance of daily portfolio returns over the period.
        :param start: str
            Start date: Example: '20070101'
        :param end: str
            End date: Example : '20180101
        :return: float
        """
        var = np.dot(self.weights.T, np.dot(self.securities_returns(start, end).cov()*252, self.weights))
        return var

    def perf(self, start: str, end: str, **kwargs):
        """

        Compute return of the portfolio over the period.
        :param start: str
            Start date: Example: '20070101'
        :param end: str
            End date: Example : '20180101
        :return: float

        """

        histo_val = self.ptf_histo_value(start, end)
        perf = histo_val[-1] / histo_val[0] - 1

        return perf

    def indices_beta(self, start: str, end: str):
        """

        Compute portfolio beta to list of major indices.

        :param start:str
            Start date
        :param end:
            End date
        :return: pd.Series

        :Example

        DAX                0.533962
        CAC 40             0.500274
        ESTX50 EUR P       0.858401
        EURONEXT 100       0.752807

        """
        indices_returns = RandomPortfolio.market_data.indices_returns[start:end]

        df = pd.concat([self.ptf_returns(start, end), indices_returns], axis=1, join='inner')
        betas = (df.cov()[0] / df.var())[1:]
        return betas


