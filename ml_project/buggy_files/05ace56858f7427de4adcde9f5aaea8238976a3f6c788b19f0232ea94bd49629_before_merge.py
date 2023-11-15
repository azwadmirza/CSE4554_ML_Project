    def __eq__(self, other):
        res = isinstance(other, self.__class__) and\
              self.has_samecoef(other) and \
              self.has_samedomain(other) and\
              self.has_samewindow(other)
        return res