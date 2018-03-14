import pytest
from EasyPortfolioExplorer.app.easy.portfolio import RandomPortfolio
from EasyPortfolioExplorer.app.utils.market_data import MarketData

ptf_param = dict(
    id=11111111111,
)

data_param = {'hdf5_file': r'EasyPortfolioExplorer\app\data\market_data.h5',
              'quandl_api_key': 'JqdF7uDhmsYofsgDN5wW',
              'key': 'market_close'

              }

@pytest.fixture(scope='module')
def mkt_data():
    data = MarketData(**data_param)
    return data


@pytest.fixture(scope='module')
def ptf():

    portfolio = RandomPortfolio(**ptf_param)
    return portfolio