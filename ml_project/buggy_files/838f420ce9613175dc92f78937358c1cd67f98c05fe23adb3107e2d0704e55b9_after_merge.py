    def __pow__(self, other):
        coef = self._pow(self.coef, other, maxpower = self.maxpower)
        res = self.__class__(coef, self.domain, self.window)
        return res