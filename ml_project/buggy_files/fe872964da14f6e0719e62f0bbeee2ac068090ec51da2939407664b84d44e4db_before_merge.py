    def decode(self, encodings=None):
        encodings = self._verify_encodings(encodings)
        comps = _decode_personname(self.components, encodings)
        return PersonName3(u'='.join(comps), encodings)