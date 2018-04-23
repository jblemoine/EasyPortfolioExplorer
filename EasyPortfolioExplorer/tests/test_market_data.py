import pandas as pd


def test_data(mkt_data):

    data = mkt_data.data

    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    assert isinstance(data.index, pd.DatetimeIndex)

    tickers_test = ['AAPL', 'MSFT', 'F']

    for ticker in tickers_test:
        assert ticker in data.columns

    assert (data.index[-1] + pd.Timedelta(days=5)) >= pd.Timestamp(mkt_data.date_max)


def test_indices_returns(mkt_data):

    data = mkt_data.indices_returns

    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    assert isinstance(data.index, pd.DatetimeIndex)

    assert (data.index[-1] + pd.Timedelta(days=5)) >= pd.Timestamp(mkt_data.date_max)





