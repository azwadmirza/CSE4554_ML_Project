    def encode(self, encodings):
        """Encode the unicode using the specified encoding"""
        encodings = self._verify_encodings(encodings)

        components = self.split('=')

        comps = [C.encode(enc) for C, enc in zip(components, encodings)]

        # Remove empty elements from the end
        while len(comps) and not comps[-1]:
            comps.pop()

        return '='.join(comps)