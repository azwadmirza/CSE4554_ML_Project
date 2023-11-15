    def __rdivmod__(self, other):
        try:
            quo, rem = self._div(other, self.coef)
        except ZeroDivisionError as e:
            raise e
        except:
            return NotImplemented
        quo = self.__class__(quo, self.domain, self.window)
        rem = self.__class__(rem, self.domain, self.window)
        return quo, rem