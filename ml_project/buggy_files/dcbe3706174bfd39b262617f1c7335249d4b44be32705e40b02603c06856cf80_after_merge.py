    def __init__(self, *args, **kwargs):
        self.__dict__['artists'] = frozenset(kwargs.pop('artists', []))
        super(Track, self).__init__(*args, **kwargs)