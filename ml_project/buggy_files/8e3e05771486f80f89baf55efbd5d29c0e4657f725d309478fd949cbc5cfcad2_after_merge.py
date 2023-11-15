    def to_doc(self, value, indent=0):
        if value is None:
            return 'empty'

        val, typ = self._val_and_type(value)
        return typ.to_doc(val)