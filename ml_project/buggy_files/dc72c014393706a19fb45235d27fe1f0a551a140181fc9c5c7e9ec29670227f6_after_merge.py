    def __init__(self, data, encoding_args):
        self.encoding_args = encoding_args
        super().__init__(data.__str__().encode(*self.encoding_args))