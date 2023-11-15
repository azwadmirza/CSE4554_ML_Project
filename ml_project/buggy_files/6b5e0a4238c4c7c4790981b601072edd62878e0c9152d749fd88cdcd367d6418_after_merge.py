    def __init__(self, data):
        super().__init__()
        self.mean = np.mean(data, axis=0)
        self.std = np.std(data, axis=0)