from datetime import date as dte

import numpy as np
import pandas as pd

from EasyPortfolioExplorer.app.easy.portfolio import RandomPortfolio
from EasyPortfolioExplorer.app.utils.resource_loader import ResourceLoader


def random_id():
    return np.random.randint(100000000000, 999999999999, dtype=np.int64).astype(str)


class Storage(ResourceLoader):

    def __init__(self, ptf_number: int, market_data, parallel=False, **kwargs):
        assert 1 < ptf_number < 2000, "ptf number must be between 1 and 2000."
        
        super().__init__(**kwargs)
        self.df = pd.DataFrame()
        self.parallel = parallel

        RandomPortfolio.set_market_data(market_data)
        self.df['Portfolio'] = [RandomPortfolio(id=random_id()) for _ in range(ptf_number)]
        self.df['id'] = self.df['Portfolio'].apply(lambda x: x.id)
        self.df['Fund_manager'] = self.df['Portfolio'].apply(lambda x: x.fund_manager)
        self.df['Client_name'] = self.df['Portfolio'].apply(lambda x: x.client)
        self.df['Type'] = self.df['Portfolio'].apply(lambda x: x.type)
        self.df['Creation_date'] = pd.to_datetime(self.df['Portfolio'].apply(lambda x: x.creation_date))

        self.date_range = pd.date_range(start=market_data.date_min, end=dte.today(), freq='BAS')

    def _compute_returns(self, start, end):
        try:
            self.df["Return_from_{0}_to_{1}".format(start, end)]

        except KeyError:
            self.df["Return_from_{0}_to_{1}".format(start, end)] = self.df['Portfolio'].apply(
                lambda x: x.perf(start, end))

    def _compute_variance(self, start, end):
        try:
            self.df["Variance_from_{0}_to_{1}".format(start, end)]

        except KeyError:
            self.df["Variance_from_{0}_to_{1}".format(start, end)] = self.df['Portfolio'].apply(
                lambda x: x.variance(start, end))




