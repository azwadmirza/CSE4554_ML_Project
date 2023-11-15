    def __init__(self, *args, **kwargs):
        self.__dict__['tracks'] = tuple(kwargs.pop('tracks', []))
        super(Playlist, self).__init__(*args, **kwargs)