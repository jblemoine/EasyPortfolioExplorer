import datetime as dt

import pandas as pd
from pandas.tseries.offsets import BDay


def test_data(mkt_data):

    data = mkt_data.data

    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    assert isinstance(data.index, pd.DatetimeIndex)

    tickers_test = ['AAPL', 'A', 'MSFT']

    for ticker in tickers_test:
        assert ticker in data.columns

    assert data.index[-1] >= (dt.date.today() - BDay(5))


def test_indices_returns(mkt_data):

    data = mkt_data.indices_returns

    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    assert isinstance(data.index, pd.DatetimeIndex)

    assert data.index[-1] >= (dt.date.today() - BDay(5))





