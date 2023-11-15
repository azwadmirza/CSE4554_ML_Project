    def from_obj(self, value):
        return str(keyutils.KeySequence.parse(value))