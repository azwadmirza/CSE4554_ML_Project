    def __init__(self, *args, **kwargs):
        self.__dict__['tracks'] = tuple(kwargs.pop('tracks', []))
        self.__dict__['artists'] = tuple(kwargs.pop('artists', []))
        self.__dict__['albums'] = tuple(kwargs.pop('albums', []))
        super(SearchResult, self).__init__(*args, **kwargs)