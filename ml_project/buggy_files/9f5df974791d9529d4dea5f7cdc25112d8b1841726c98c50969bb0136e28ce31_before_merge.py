    def isket(self):
        return isinstance(self.dims[0], list) and np.prod(self.dims[1]) == 1