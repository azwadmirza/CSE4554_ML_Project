    def __mul__(self, other):
        try:
            othercoef = self._get_coefficients(other)
            coef = self._mul(self.coef, othercoef)
        except TypeError as e:
            raise e
        except:
            return NotImplemented
        return self.__class__(coef, self.domain, self.window)