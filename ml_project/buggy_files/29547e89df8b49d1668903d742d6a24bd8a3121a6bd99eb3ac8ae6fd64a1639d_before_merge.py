    def size(self):
        """Numpy-style attribute giving the total dataset size"""
        return numpy.prod(self.shape, dtype=numpy.intp)