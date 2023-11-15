    def _verify_encodings(self, encodings):
        """Checks the encoding to ensure proper format"""
        if encodings is None:
            return self.encodings

        if not isinstance(encodings, list):
            encodings = [encodings]

        return encodings