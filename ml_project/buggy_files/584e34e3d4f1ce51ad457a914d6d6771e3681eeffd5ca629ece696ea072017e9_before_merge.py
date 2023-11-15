    def isbra(self):
        return isinstance(self.dims[1], list) and np.prod(self.dims[0]) == 1