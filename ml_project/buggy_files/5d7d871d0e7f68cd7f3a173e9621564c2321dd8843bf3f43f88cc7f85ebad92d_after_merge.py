    def to_str(self, value):
        if value is None:
            return ''

        val, typ = self._val_and_type(value)
        return typ.to_str(val)