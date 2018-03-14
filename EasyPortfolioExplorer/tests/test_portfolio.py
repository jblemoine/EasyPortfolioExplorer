import numpy as np
import pandas as pd
import pytest

return_param = dict(
    start='20080101',
    end='20180101',
    tickers=['AAPL', 'A', 'F', 'GS']
)


def test_set_market_data(ptf, mkt_data):

    ptf.set_market_data(mkt_data)
    assert isinstance(ptf.raw_data, pd.DataFrame)


def test_weight(ptf):
    assert ptf.weights.size


def test_return(ptf):

    ptf.size = len(return_param['tickers'])
    ptf.tickers = return_param['tickers']
    random_arr = np.random.randint(10, size=ptf.size)
    ptf.weights = random_arr / random_arr.sum()

    df = ptf.raw_data.loc[return_param['start']:return_param['end'], return_param['tickers']]
    true_perf = (df.iloc[-1] / df.iloc[0] - 1).dot(ptf.weights)

    assert ptf.perf(start=return_param['start'], end=return_param['end']) == pytest.approx(true_perf, rel=1e-5)


