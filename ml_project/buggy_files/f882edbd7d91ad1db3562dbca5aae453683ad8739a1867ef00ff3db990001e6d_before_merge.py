    def encode(self, encodings=None):
        encodings = self._verify_encodings(encodings)

        if isinstance(self.components[0], bytes):
            comps = self.components
        else:
            comps = [
                C.encode(enc) for C, enc in zip(self.components, encodings)
            ]

        # Remove empty elements from the end
        while len(comps) and not comps[-1]:
            comps.pop()

        return b'='.join(comps)