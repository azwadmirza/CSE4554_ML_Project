    def __init__(self, types):
        self.types = tuple(types)
        self.count = len(self.types)
        self.dtype = UnionType(types)
        name = "Tuple(%s)" % ', '.join(str(i) for i in self.types)
        super(Tuple, self).__init__(name)