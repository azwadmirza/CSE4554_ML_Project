    def __init__(self, data, encoding_args):
        self.encoding_args = encoding_args
        super().__init__(data.encode(*self.encoding_args))