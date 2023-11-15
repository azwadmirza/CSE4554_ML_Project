    def from_obj(self, value):
        if value is None:
            return []
        return [self.valtype.from_obj(v) for v in value]