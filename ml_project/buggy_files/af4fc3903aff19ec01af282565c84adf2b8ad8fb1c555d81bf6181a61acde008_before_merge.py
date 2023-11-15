    def __iter__(self):
      raise TypeError("'{}' object is not iterable".format(type(self).__name__))