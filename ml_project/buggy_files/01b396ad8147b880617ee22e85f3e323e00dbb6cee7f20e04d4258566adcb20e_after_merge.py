    def __init__(self):
        from . import API_VERSION
        self.base_uri = 'https://api.themoviedb.org'
        self.base_uri += '/{version}'.format(version=API_VERSION)