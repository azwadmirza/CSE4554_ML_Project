    def __init__(self, *args, **kwargs):
        self.__dict__['artists'] = frozenset(kwargs.pop('artists', []))
        self.__dict__['images'] = frozenset(kwargs.pop('images', []))
        super(Album, self).__init__(*args, **kwargs)