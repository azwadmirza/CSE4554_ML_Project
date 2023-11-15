    def __init__(self, val, encodings):
        self.encodings = self._verify_encodings(encodings)
        PersonNameBase.__init__(self, val)