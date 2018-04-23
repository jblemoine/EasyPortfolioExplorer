import pytest
import os
import sys
current_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
folder = os.path.dirname(current_folder)
sys.path.append(folder)
from EasyPortfolioExplorer import RandomPortfolio
from EasyPortfolioExplorer import MarketData


ptf_param = dict(
    id=11111111111,
)

data_param = {'hdf5_file': r'EasyPortfolioExplorer\app\data\market_data.h5',
              'quandl_api_key': 'JqdF7uDhmsYofsgDN5wW',
              'key': 'market_close',
              'date_max': '20180401'

              }


@pytest.fixture(scope='module')
def mkt_data():
    data = MarketData(**data_param)
    return data


@pytest.fixture(scope='module')
def ptf():

    portfolio = RandomPortfolio(**ptf_param)
    return portfolio

