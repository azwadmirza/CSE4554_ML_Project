    def __init__(self, val, encodings=default_encoding):
        if isinstance(val, PersonName3):
            encodings = val.encodings
            val = val.original_string

        self.original_string = val

        self.encodings = self._verify_encodings(encodings)
        self.parse(val)