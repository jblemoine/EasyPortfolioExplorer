import dash


class EasyBase:

    def __init__(self,
                 server=None,
                 url_base_pathname='/',
                 debug=False, **kwargs
                 ):
        self.app = dash.Dash(sever=server, url_base_pathname=url_base_pathname)
        self._debug = debug
        self.app.title = 'Easy Portfolio Explorer'
        self.app.config.supress_callback_exceptions = True




