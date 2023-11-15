    def __init__(self, *args, **kwargs):
        # NOTE kwargs dict keys must be bytestrings to work on Python < 2.6.5
        # See https://github.com/mopidy/mopidy/issues/302 for details
        self.__dict__[b'tracks'] = tuple(kwargs.pop('tracks', []))
        super(Playlist, self).__init__(*args, **kwargs)