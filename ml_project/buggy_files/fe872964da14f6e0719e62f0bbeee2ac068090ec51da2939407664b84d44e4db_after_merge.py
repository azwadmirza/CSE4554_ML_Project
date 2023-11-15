    def decode(self, encodings=None):
        encodings = _verify_encodings(encodings) or self.encodings
        comps = _decode_personname(self.components, encodings)
        return PersonName3(u'='.join(comps), encodings)