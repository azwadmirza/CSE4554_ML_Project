    def __rmod__(self, other):
        try:
            quo, rem = self._div(other, self.coef)
        except:
            return NotImplemented
        return self.__class__(rem, self.domain, self.window)