import numpy as np
import pandas as pd
from datetime import date as dte

from .portfolio import RandomPortfolio
from EasyPortfolioExplorer.app.utils.resource_loader import ResourceLoader


def random_id():
    return np.random.randint(100000000000, 999999999999, dtype=np.int64).astype(str)


class Storage(ResourceLoader):
    """
        Singleton class. It serves as an intermediate storage facilities of portfolios information between callbacks.
    Data is stored in a DataFrame.
    """

    def __init__(self, ptf_number: int, market_data, **kwargs):
        assert 1 < ptf_number < 2000, "ptf number must be between 1 and 2000."
        
        super().__init__(**kwargs)
        self.df = pd.DataFrame()

        RandomPortfolio.set_market_data(market_data)
        self.df['Portfolio'] = [RandomPortfolio(id=random_id()) for _ in range(ptf_number)]
        self.df['id'] = self.df['Portfolio'].apply(lambda x: x.id)
        self.df['Fund_manager'] = self.df['Portfolio'].apply(lambda x: x.fund_manager)
        self.df['Client_name'] = self.df['Portfolio'].apply(lambda x: x.client)
        self.df['Type'] = self.df['Portfolio'].apply(lambda x: x.type)
        self.df['Creation_date'] = pd.to_datetime(self.df['Portfolio'].apply(lambda x: x.creation_date))

        self.date_range = pd.date_range(start=market_data.date_min, end=dte.today(), freq='BAS')

    def _compute_returns(self, start, end):
        """
        Compute return over the period for every portfolio in the Storage DataFrame.
        Store the result for the session in the Storage DataFrame.

        :param start: start date
        :param end: end date
        :return: None
        """
        try:
            self.df["Return_from_{0}_to_{1}".format(start, end)]

        except KeyError:
            self.df["Return_from_{0}_to_{1}".format(start, end)] = self.df['Portfolio'].apply(
                lambda x: x.perf(start, end))

    def _compute_variance(self, start, end):
        """
        Compute variance over the period for every portfolio in the Storage DataFrame.
        Store the result for the session in the Storage DataFrame.

        :param start:
        :param end:
        :return: None
        """
        try:
            self.df["Variance_from_{0}_to_{1}".format(start, end)]

        except KeyError:
            self.df["Variance_from_{0}_to_{1}".format(start, end)] = self.df['Portfolio'].apply(
                lambda x: x.variance(start, end))




