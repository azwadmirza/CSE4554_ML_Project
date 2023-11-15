    def __rtruediv__(self, other):
        # there is no true divide if the rhs is not a scalar, although it
        # could return the first n elements of an infinite series.
        # It is hard to see where n would come from, though.
        if len(self.coef) == 1:
            try:
                quo, rem = self._div(other, self.coef[0])
            except:
                return NotImplemented
        return self.__class__(quo, self.domain, self.window)