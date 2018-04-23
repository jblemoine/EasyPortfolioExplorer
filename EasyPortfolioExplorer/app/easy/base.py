import dash


class EasyBase:
    """
    The base class of the app.
    There is room for adding a Flask server.
    """

    def __init__(self,
                 url_base_pathname='/',
                 debug=False,
                 **kwargs
                 ):
        self.app = dash.Dash(url_base_pathname=url_base_pathname)
        self._debug = debug
        self.app.title = 'Easy Portfolio Explorer'
        self.app.config.supress_callback_exceptions = True




