    def __call__(self, inst):
        value = inst[inst.domain.index(self.column)]
        if self.values is None:
            return not isnan(value)
        else:
            return value in self.values