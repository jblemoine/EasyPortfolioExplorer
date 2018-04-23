import datetime as dt
from time import sleep
import fix_yahoo_finance as yf
import pandas as pd
import quandl
from pandas_datareader import data as pdr
from quandl.errors.quandl_error import LimitExceededError
import os
from EasyPortfolioExplorer.app.static.major_indices import INDICES


class MarketData:
    """
    Container for market data. Retrieve and aggregate market data from Quandl and Yahoo Finance.

    """

    def __init__(self, hdf5_file,
                 key=None,
                 date_min='19990101',
                 date_max=dt.date.today().strftime("%Y%m%d"),
                 quandl_api_key=None):

        self._data = None
        self._indices_returns = None
        self.date_min = date_min
        self.date_max = date_max
        self.file = hdf5_file

        # A new file is going to be created,
        # so the directory should be writable.
        parentname = os.path.dirname(self.file)
        if not parentname:
            parentname = '.'
        if not os.access(parentname, os.F_OK):
            raise IOError("``%s`` does not exist" % (parentname,))
        if not os.path.isdir(parentname):
            raise IOError("``%s`` is not a directory" % (parentname,))
        if not os.access(parentname, os.W_OK):
            raise IOError("directory ``%s`` exists but it can not be "
                          "written" % (parentname,))

        self.key = key
        self.api_key = quandl_api_key

        if self.api_key:
            quandl.ApiConfig.api_key = self.api_key

        connected = False
        while not connected:
            try:
                self.wiki_columns = list(quandl.get_table('WIKI/PRICES', date='2018-01-01').columns)
                connected = True
            except LimitExceededError:
                sleep(10)

        self.securities = list(self.data.columns)

    @property
    def data(self):
        """

        DataFrame with close prices. Index is date, columns are tickers.

        :return: DataFrame with the following template:


                    A 	        AA 	        AAL
        date
        2007-01-02 	23.400856 	23.000      146.28666

        """

        # Fist check if file located, if not bulk download from quandl
        if self._data is None:
            try:
                self._data = pd.read_hdf(self.file, key=self.key, where=["index>{}".format(self.date_min)])

            except (FileNotFoundError, OSError):
                self.import_bulk_data()
                self.export_data(self._data, key=self.key)

        #
        if (self._data.index[-1] + pd.Timedelta(days=5)) < pd.Timestamp(self.date_max):

            self.update_data()
            self.export_data(df=self._data, key=self.key)
            self._data = self._data[self.date_min:self.date_max]

        return self._data

    def export_data(self, df: pd.DataFrame, key: str):
        df.to_hdf(self.file, key=key, format='table')

    def _adjust_frame_format(self, df: pd.DataFrame):
        """

        Clean data downloaded from quandl request and adjust format. We are only interested in closed_price column.

        :param df: Output of quandl request.
        :return: A cleaned DataFrame with the following template:


                    A 	        AA 	        AAL
        date
        2007-01-02 	23.400856 	23.000      146.28666

        """

        try:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index(keys='date', inplace=True)

        except KeyError:
            pass

        assert isinstance(df.index, pd.DatetimeIndex), 'index must be pandas DatetimeIndex '

        merged_df = pd.concat([df.loc[(df['ticker'] == ticker), ['adj_close']] for ticker in df.ticker.unique()],
                              axis=1)
        merged_df.columns = df.ticker.unique()

        merged_df = self.check_data_integrity(merged_df)

        return merged_df

    @staticmethod
    def check_data_integrity(df):

        df.dropna(axis=1, thresh=int(df.shape[0]/2), inplace=True)
        df = df.fillna(method='bfill').fillna(method='ffill')

        # remove stocks with abnormal pchange i.e non-adjusted close price
        pct_change = df.pct_change()
        spurious_count = pct_change[pct_change > 1].count()
        stocks = spurious_count[spurious_count == 0].index

        df = df[stocks]
        df = df.astype('float32')

        return df

    def update_data(self):
        """

        Download market data with quandl API.

        :return: A DataFrame with latest close prices.
        """

        print("Retrieve data from quandl...")
        new_data = None

        while new_data is None:
            try:
                new_data = quandl.get_table('WIKI/PRICES', qopts={'columns': ['date', 'ticker', 'adj_close', 'adj_volume']},
                                    date={'gte': self._data.index[-1].strftime('%Y-%m-%d'),
                                          'lte': dt.date.today().strftime('%Y-%m-%d')}, paginate=True)
            except LimitExceededError:
                sleep(10)
        print("Data downloaded.")

        new_data = self._adjust_frame_format(new_data)
        self._data = pd.concat([self._data, new_data]).groupby(level=0).last()
        self._data = self._data[~self._data.index.duplicated(keep='first')]

    def import_bulk_data(self):

        print("Bulk download from Quandl, it might takes time.")
        quandl.bulkdownload("WIKI")
        print('File downloaded as WIKI.zip.')

        print('Reading zip file...')
        bulk_data = pd.read_csv('./WIKI.zip',
                    usecols=['ticker', 'adj_close', 'adj_volume', 'date'],
                    dtype={'ticker': 'category', 'adj_close': 'float32', 'adj_volume': 'float32'},
                    parse_dates=['date'],
                    names=self.wiki_columns
                                )

        self._data = self._adjust_frame_format(bulk_data)
        self._data = self.check_data_integrity(self._data)
        del bulk_data

    def update_indices_returns(self):
        """

        Get major indices prices from Yahoo.

        :return: None
        """

        start_date = pd.Timestamp(self.date_min).strftime('%Y-%m-%d')
        end_date = pd.Timestamp(self.date_max).strftime('%Y-%m-%d')
        yf.pdr_override()
        data = pdr.get_data_yahoo(list(INDICES.values()), start=start_date, end=end_date, group_by='ticker')
        close = pd.concat([data[ticker]['Adj Close'] for ticker in data.items], axis=1)
        close = close.fillna(method='ffill').fillna(method='bfill')
        close.columns = INDICES.keys()

        close.dropna(how='all', axis=1, inplace=True)

        self._indices_returns = close / close.shift(1) - 1
        self.export_data(self._indices_returns, key='indices_data')

    @property
    def indices_returns(self):

        try:
            self._indices_returns = pd.read_hdf(self.file, key='indices_data')
        except (FileNotFoundError, KeyError):
            self.update_indices_returns()

        else:
            if (self._indices_returns.index[-1] + pd.Timedelta(days=5)) < pd.Timestamp(self.date_max):
                self.update_indices_returns()

        return self._indices_returns
