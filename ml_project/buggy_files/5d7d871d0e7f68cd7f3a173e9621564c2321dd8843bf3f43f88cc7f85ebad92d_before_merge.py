    def to_str(self, value):
        if value is None:
            return ''

        if isinstance(value, list):
            if len(value) == 1:
                return self.valtype.to_str(value[0])
            else:
                return self.listtype.to_str(value)
        else:
            return self.valtype.to_str(value)