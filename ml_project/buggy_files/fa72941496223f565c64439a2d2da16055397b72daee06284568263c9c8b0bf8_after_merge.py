    def __call__(self, inst):
        value = inst[inst.domain.index(self.column)]
        if self.case_sensitive:
            return value in self._values
        else:
            return value.lower() in self.values_lower