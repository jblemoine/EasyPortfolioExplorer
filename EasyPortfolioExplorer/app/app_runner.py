import sys
sys.path.append(r'C:\Users\Jean-Baptiste\Google Drive\Python\EasyPortfolioExplorer\EasyPortfolioExplorer')

from easy.callbacks import EasyCallbacks
from utils.market_data import MarketData


def init():

    market_data = MarketData("data/market_data.h5", key='market_close', date_min='20070101', date_max='20180309',
                             quandl_api_key='JqdF7uDhmsYofsgDN5wW')


    return EasyCallbacks(
        url_base_pathname='/',
        debug=True,
        market_data=market_data,
        ptf_number=100,
        labels=['Fund_manager', 'Creation_date', 'Type']
    ).app


def main():

    server = init()
    server.run_server(
        debug=True
    )

if __name__ == '__main__':
    main()
