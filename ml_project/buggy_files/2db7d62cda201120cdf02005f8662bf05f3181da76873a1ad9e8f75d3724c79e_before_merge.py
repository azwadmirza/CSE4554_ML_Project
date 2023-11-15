    def __truediv__(self, other):
        # there is no true divide if the rhs is not a scalar, although it
        # could return the first n elements of an infinite series.
        # It is hard to see where n would come from, though.
        if np.isscalar(other):
            # this might be overly restrictive
            coef = self.coef/other
            return self.__class__(coef, self.domain, self.window)
        else:
            return NotImplemented