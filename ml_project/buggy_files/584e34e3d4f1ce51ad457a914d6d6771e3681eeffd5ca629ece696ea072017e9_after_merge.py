    def isbra(self):
        return (np.prod(self.dims[0]) == 1 and
                isinstance(self.dims[1], list) and
                isinstance(self.dims[1][0], int))