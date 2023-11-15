    def to_doc(self, value, indent=0):
        if value is None:
            return 'empty'

        if isinstance(value, list):
            if len(value) == 1:
                return self.valtype.to_doc(value[0], indent)
            else:
                return self.listtype.to_doc(value, indent)
        else:
            return self.valtype.to_doc(value, indent)