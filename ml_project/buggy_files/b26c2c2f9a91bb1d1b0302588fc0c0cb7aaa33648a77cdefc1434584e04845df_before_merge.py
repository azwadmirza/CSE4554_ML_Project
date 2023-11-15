    def __getitem__(self, key):
        return type(self)(self.array[key])