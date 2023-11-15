    def __init__(self, *args, **kwargs):
        self.__dict__['artists'] = frozenset(kwargs.pop('artists', []))
        super(Album, self).__init__(*args, **kwargs)