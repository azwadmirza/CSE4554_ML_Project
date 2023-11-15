    def reshape(self, *args, **kwargs):
        """
        See numpy.ndarray.reshape
        """
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            shape = args[0]
        else:
            shape = args

        if tuple(shape) == self.shape:
            # XXX ignoring the "order" keyword.
            return self

        return self.values.reshape(shape, **kwargs)