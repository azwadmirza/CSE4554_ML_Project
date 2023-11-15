    def __init__(self, dtype, count):
        self.dtype = dtype
        self.count = count
        name = "UniTuple(%s x %d)" % (dtype, count)
        super(UniTuple, self).__init__(name)