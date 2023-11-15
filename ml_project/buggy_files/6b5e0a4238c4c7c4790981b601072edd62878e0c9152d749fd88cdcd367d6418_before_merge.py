    def __init__(self, data):
        super().__init__()
        self.max_val = data.max()
        data = data / self.max_val
        self.mean = np.mean(data, axis=0, keepdims=True).flatten()
        self.std = np.std(data, axis=0, keepdims=True).flatten()