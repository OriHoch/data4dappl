class FeedMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if self.is_atom_feed(environ['PATH_INFO']):
            def _start_response(status, headers, exc_info=None):
                return start_response(status, self.set_charset(headers), exc_info)
        else:
            _start_response = start_response
        return self.app(environ, _start_response)

    @staticmethod
    def set_charset(headers, charset='utf-8'):
        for header in headers:
            attr, value = header
            if attr.lower() == 'content-type':
                if '; ' not in value:
                    value += '; charset={}'.format(charset)
            yield (attr, value)

    @staticmethod
    def is_atom_feed(path_info):
        return path_info.startswith('/feeds/') and path_info.endswith('.atom')
