    def __mod__(self, other):
        if isinstance(other, ABCPolyBase):
            if not self.has_sametype(other):
                raise TypeError("Polynomial types differ")
            elif not self.has_samedomain(other):
                raise TypeError("Domains differ")
            elif not self.has_samewindow(other):
                raise TypeError("Windows differ")
            else:
                quo, rem = self._div(self.coef, other.coef)
        else:
            try:
                quo, rem = self._div(self.coef, other)
            except:
                return NotImplemented
        return self.__class__(rem, self.domain, self.window)