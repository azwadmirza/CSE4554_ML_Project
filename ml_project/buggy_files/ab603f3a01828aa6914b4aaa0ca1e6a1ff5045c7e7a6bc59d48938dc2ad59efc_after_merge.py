    def __init__(self, types):
        self.types = tuple(types)
        self.count = len(self.types)
        self.dtype = UnionType(types)
        name = "%s(%s)" % (
            self.__class__.__name__,
            ', '.join(str(i) for i in self.types),
        )
        super(Tuple, self).__init__(name)