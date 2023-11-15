    def isket(self):
        return (np.prod(self.dims[1]) == 1 and
                isinstance(self.dims[0], list) and
                isinstance(self.dims[0][0], int))