    def __init__(self, val, encodings=None, original_string=None):
        if isinstance(val, PersonName3):
            encodings = val.encodings
            self.original_string = val.original_string
            self._components = tuple(str(val).split('='))
        elif isinstance(val, bytes):
            # this is the raw byte string - decode it on demand
            self.original_string = val
            self._components = None
        else:
            # handle None `val` as empty string
            val = val or ''

            # this is the decoded string - save the original string if
            # available for easier writing back
            self.original_string = original_string
            self._components = tuple(val.split('='))

        # if the encoding is not given, leave it as undefined (None)
        self.encodings = _verify_encodings(encodings)
        self._dict = {}