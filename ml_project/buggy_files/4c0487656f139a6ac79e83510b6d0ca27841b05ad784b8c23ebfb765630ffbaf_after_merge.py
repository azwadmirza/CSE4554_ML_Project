    def __init__(self, original, delete=None):
        super(AdjacentTempDirectory, self).__init__(delete=delete)
        self.original = original.rstrip('/\\')