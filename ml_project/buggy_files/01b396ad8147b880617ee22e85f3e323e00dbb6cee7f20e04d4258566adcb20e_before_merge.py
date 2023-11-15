    def __init__(self):
        from . import API_VERSION, REQUESTS_SESSION, __version__
        self.base_uri = 'https://api.themoviedb.org'
        self.base_uri += '/{version}'.format(version=API_VERSION)
        self.session = REQUESTS_SESSION or requests.Session()
        self.session.headers.setdefault('user-agent', 'tmdb_api/{}.{}.{}'.format(*__version__))