    def __rfloordiv__(self, other):
        try:
            quo, rem = self._div(other, self.coef)
        except:
            return NotImplemented
        return self.__class__(quo, self.domain, self.window)