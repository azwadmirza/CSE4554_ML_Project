    def __getitem__(self, key):
        return type(self)(_wrap_numpy_scalars(self.array[key]))