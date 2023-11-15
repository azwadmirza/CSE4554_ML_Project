    def size(self):
        """Numpy-style attribute giving the total dataset size"""
        if is_empty_dataspace(self.id):
            return None
        return numpy.prod(self.shape, dtype=numpy.intp)