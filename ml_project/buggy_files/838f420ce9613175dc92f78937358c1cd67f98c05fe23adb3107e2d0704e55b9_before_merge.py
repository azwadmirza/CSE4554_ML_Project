    def __pow__(self, other):
        try:
            coef = self._pow(self.coef, other, maxpower = self.maxpower)
        except:
            raise
        return self.__class__(coef, self.domain, self.window)