import datetime as dt
from time import sleep
import fix_yahoo_finance as yf
import pandas as pd
import quandl
from pandas.tseries.offsets import BDay
from pandas_datareader import data as pdr
from quandl.errors.quandl_error import LimitExceededError

from static.major_indices import INDICES


class MarketData:

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
        self.key = key
        self.api_key = quandl_api_key

        if self.api_key:
            quandl.ApiConfig.api_key = self.api_key

        self.securities = list(self.data.columns)

        connected = False
        while not connected:
            try:
                self.wiki_columns = list(quandl.get_table('WIKI/PRICES', date='2018-01-01').columns)
                connected = True
            except LimitExceededError:
                sleep(10)

    @property
    def data(self):
        if self._data is None:
            try:
                self._data = pd.read_hdf(self.file, key=self.key, where=["index>{}".format(self.date_min)])

            except (FileNotFoundError, OSError):
                self.import_bulk_data()
                self.export_data(self._data, key=self.key)

        if self._data.index[-1] < pd.Timestamp(self.date_max) and self._data.index[-1] < (dt.date.today() - BDay(5)):

            self.update_data()
            self.export_data(self._data, key=self.key)
            self._data = self._data[self.date_min:self.date_max]

        return self._data

    def export_data(self, df: pd.DataFrame, key: str):
        df.to_hdf(self.file, key=key, format='table')

    @staticmethod
    def _adjust_frame_format(df: pd.DataFrame):

        try:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index(keys='date', inplace=True)

        except KeyError:
            pass

        assert isinstance(df.index, pd.DatetimeIndex), 'index must be pandas DatetimeIndex '

        merged_df = pd.concat([df.loc[(df['ticker'] == ticker), ['adj_close']] for ticker in df.ticker.unique()],
                              axis=1).fillna(method='bfill').fillna(method='ffill')
        merged_df.columns = df.ticker.unique()

        # remove stocks with abnormal pchange i.e non-adjusted close price
        pct_change = merged_df.pct_change()
        spurious_count = pct_change[pct_change > 1].count()
        stocks = spurious_count[spurious_count == 0].index

        merged_df = merged_df[stocks]
        merged_df = merged_df.astype('float32')

        return merged_df

    def update_data(self):

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

    def import_bulk_data(self):

        print("Bulk download from Quandl, might take time.")
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
        del bulk_data

    def update_indices_returns(self):

        start_date = pd.Timestamp(self.date_min).strftime('%Y-%m-%d')
        end_date = pd.Timestamp(self.date_max).strftime('%Y-%m-%d')
        yf.pdr_override()
        data = pdr.get_data_yahoo(list(INDICES.values()), start=start_date, end=end_date, group_by='ticker',
                                  threads=len(INDICES), )
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
            if self._indices_returns.index[-1] < pd.Timestamp(self.date_max):
                self.update_indices_returns()

        return self._indices_returns
