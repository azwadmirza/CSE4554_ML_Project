    def encode(self, encodings=None):
        encodings = _verify_encodings(encodings) or self.encodings
        return _encode_personname(self.components, encodings)