from easy.base import EasyBase


class ResourceLoader(EasyBase):

    def __init__(self, **kwargs):
        super(ResourceLoader, self).__init__(**kwargs)

        self._css_urls = [
            'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
            'https://drive.google.com/uc?export=download&id=1WI1tctnEiLySSMkCQwaOObuZiF2UmLi2',

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
