    def encode(self, encodings):
        """Encode the unicode using the specified encoding"""
        encodings = _verify_encodings(encodings) or self.encodings
        return _encode_personname(self.split('='), encodings)