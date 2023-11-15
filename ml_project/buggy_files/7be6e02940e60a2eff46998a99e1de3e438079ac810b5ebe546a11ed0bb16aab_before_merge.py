    def __init__(self, bucket, key, **kwargs):
        session = boto3.Session(profile_name=kwargs.pop('profile_name', None))
        s3 = session.resource('s3', **kwargs)
        self._object = s3.Object(bucket, key)
        self._raw_reader = RawReader(self._object)
        self._content_length = self._object.content_length
        self._current_pos = 0
        self._buffer = b''
        self._eof = False

        #
        # This member is part of the io.BufferedIOBase interface.
        #
        self.raw = None