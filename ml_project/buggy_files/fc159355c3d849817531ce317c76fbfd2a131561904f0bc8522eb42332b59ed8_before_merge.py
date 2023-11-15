    def __getitem__(self, item):
        return type(self)(self.table[item])