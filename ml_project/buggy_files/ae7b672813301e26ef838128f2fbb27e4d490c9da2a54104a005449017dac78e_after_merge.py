    def __init__(self, val, encodings=None):
        if isinstance(val, PersonName3):
            encodings = val.encodings
            val = val.original_string

        self.original_string = val

        self.encodings = _verify_encodings(encodings) or [default_encoding]
        self.parse(val)