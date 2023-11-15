    def __add__(self, other):
        if isinstance(other, ABCPolyBase):
            if not self.has_sametype(other):
                raise TypeError("Polynomial types differ")
            elif not self.has_samedomain(other):
                raise TypeError("Domains differ")
            elif not self.has_samewindow(other):
                raise TypeError("Windows differ")
            else:
                coef = self._add(self.coef, other.coef)
        else:
            try:
                coef = self._add(self.coef, other)
            except:
                return NotImplemented
        return self.__class__(coef, self.domain, self.window)