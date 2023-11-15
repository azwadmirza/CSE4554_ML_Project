    def __init__(self, dtype, count):
        self.dtype = dtype
        self.count = count
        name = "tuple(%s x %d)" % (dtype, count)
        super(UniTuple, self).__init__(name)