    def reshape(self, newshape, order='C'):
        """
        See numpy.ndarray.reshape
        """
        if order not in ['C', 'F']:
            raise TypeError(
                "must specify a tuple / singular length to reshape")

        if isinstance(newshape, tuple) and len(newshape) > 1:
            return self.values.reshape(newshape, order=order)
        else:
            return ndarray.reshape(self, newshape, order)