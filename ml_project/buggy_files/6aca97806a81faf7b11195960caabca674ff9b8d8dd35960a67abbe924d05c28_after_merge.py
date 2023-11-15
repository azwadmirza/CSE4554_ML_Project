    def __init__(self, *args, **kwargs):
        # NOTE kwargs dict keys must be bytestrings to work on Python < 2.6.5
        # See https://github.com/mopidy/mopidy/issues/302 for details
        if len(args) == 2 and len(kwargs) == 0:
            kwargs[b'tlid'] = args[0]
            kwargs[b'track'] = args[1]
            args = []
        super(TlTrack, self).__init__(*args, **kwargs)