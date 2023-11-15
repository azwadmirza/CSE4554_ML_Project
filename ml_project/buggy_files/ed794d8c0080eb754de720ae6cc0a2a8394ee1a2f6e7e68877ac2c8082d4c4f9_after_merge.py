    def __divmod__(self, other):
        try:
            othercoef = self._get_coefficients(other)
            quo, rem = self._div(self.coef, othercoef)
        except (TypeError, ZeroDivisionError) as e:
            raise e
        except:
            return NotImplemented
        quo = self.__class__(quo, self.domain, self.window)
        rem = self.__class__(rem, self.domain, self.window)
        return quo, rem