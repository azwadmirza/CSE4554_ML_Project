    def __init__(self, dtype, count):
        self.dtype = dtype
        self.count = count
        name = "%s(%s x %d)" % (
            self.__class__.__name__, dtype, count,
        )
        super(UniTuple, self).__init__(name)