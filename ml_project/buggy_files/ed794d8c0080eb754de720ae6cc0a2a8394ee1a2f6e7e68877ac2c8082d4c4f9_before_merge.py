    def __divmod__(self, other):
        if isinstance(other, self.__class__):
            if not self.has_samedomain(other):
                raise TypeError("Domains are not equal")
            elif not self.has_samewindow(other):
                raise TypeError("Windows are not equal")
            else:
                quo, rem = self._div(self.coef, other.coef)
        else:
            try:
                quo, rem = self._div(self.coef, other)
            except:
                return NotImplemented
        quo = self.__class__(quo, self.domain, self.window)
        rem = self.__class__(rem, self.domain, self.window)
        return quo, rem