    def __call__(self, inst):
        # the function is a large 'switch'; pylint: disable=too-many-branches
        value = inst[inst.domain.index(self.column)]
        if self.oper == self.IsDefined:
            return not np.isnan(value)
        if self.case_sensitive:
            value = str(value)
            refval = str(self.ref)
        else:
            value = str(value).lower()
            refval = str(self.ref).lower()
        if self.oper == self.Equal:
            return value == refval
        if self.oper == self.NotEqual:
            return value != refval
        if self.oper == self.Less:
            return value < refval
        if self.oper == self.LessEqual:
            return value <= refval
        if self.oper == self.Greater:
            return value > refval
        if self.oper == self.GreaterEqual:
            return value >= refval
        if self.oper == self.Contains:
            return refval in value
        if self.oper == self.StartsWith:
            return value.startswith(refval)
        if self.oper == self.EndsWith:
            return value.endswith(refval)
        high = self.max if self.case_sensitive else self.max.lower()
        if self.oper == self.Between:
            return refval <= value <= high
        if self.oper == self.Outside:
            return not refval <= value <= high
        raise ValueError("invalid operator")