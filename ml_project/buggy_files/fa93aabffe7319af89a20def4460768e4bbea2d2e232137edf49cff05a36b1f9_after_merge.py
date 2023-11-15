    def __repr__(self):
        return ("%s(%r, func=%r, dtype=%r)" %
                (type(self).__name__, self.array, self.func, self.dtype))