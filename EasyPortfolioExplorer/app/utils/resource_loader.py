from EasyPortfolioExplorer.app.easy.base import EasyBase


class ResourceLoader(EasyBase):
    """
    Class for adding external resources such as css and js file.
    The current version is based on boostrap 3.3.7.

    """

    def __init__(self, **kwargs):
        super(ResourceLoader, self).__init__(**kwargs)

        self._css_urls = [
            'https://cdn.rawgit.com/jblemoine/EasyPortfolioExplorer/117125bb/EasyPortfolioExplorer/app/static/extra.css',
            'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
        ]
        self._js_urls = [
            'https://code.jquery.com/'
            'jquery-3.1.1.slim.min.js',
            'https://maxcdn.bootstrapcdn.com/'
            'bootstrap/3.3.7/js/bootstrap.min.js',
            '/static/extra.js'
        ]

    def load_resources(self):

        for url in self._css_urls:
            self.app.css.append_css({'external_url': url})

        for url in self._js_urls:
            self.app.scripts.append_script({'external_url': url})