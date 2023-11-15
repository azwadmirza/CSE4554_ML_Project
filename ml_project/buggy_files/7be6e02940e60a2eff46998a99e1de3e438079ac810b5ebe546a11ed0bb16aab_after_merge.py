    def __init__(self, bucket, key, buffer_size=DEFAULT_BUFFER_SIZE,
                 line_terminator=BINARY_NEWLINE, **kwargs):
        session = boto3.Session(profile_name=kwargs.pop('profile_name', None))
        s3 = session.resource('s3', **kwargs)
        self._object = s3.Object(bucket, key)
        self._raw_reader = RawReader(self._object)
        self._content_length = self._object.content_length
        self._current_pos = 0
        self._buffer = b''
        self._eof = False
        self._buffer_size = buffer_size
        self._line_terminator = line_terminator

        #
        # This member is part of the io.BufferedIOBase interface.
        #
        self.raw = None