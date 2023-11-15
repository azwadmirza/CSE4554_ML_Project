    def __call__(self, inst):
        value = inst[inst.domain.index(self.column)]
        if isnan(value):
            return self.oper == self.Equal and isnan(self.ref)
        if self.oper == self.Equal:
            return value == self.ref
        if self.oper == self.NotEqual:
            return value != self.ref
        if self.oper == self.Less:
            return value < self.ref
        if self.oper == self.LessEqual:
            return value <= self.ref
        if self.oper == self.Greater:
            return value > self.ref
        if self.oper == self.GreaterEqual:
            return value >= self.ref
        if self.oper == self.Between:
            return self.ref <= value <= self.max
        if self.oper == self.Outside:
            return not self.ref <= value <= self.max
        if self.oper == self.IsDefined:
            return True
        raise ValueError("invalid operator")