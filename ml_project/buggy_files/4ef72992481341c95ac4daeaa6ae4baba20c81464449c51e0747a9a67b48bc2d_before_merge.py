    def setup(self):
        N = 10 ** 5
        na = np.arange(int(N / 2))
        self.left = np.concatenate([na[: int(N / 4)], na[: int(N / 4)]])
        self.right = np.concatenate([na, na])