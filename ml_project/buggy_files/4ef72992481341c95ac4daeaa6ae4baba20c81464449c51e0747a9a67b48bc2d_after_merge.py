    def setup(self, N):
        data = np.arange(N, dtype=float)
        data[40] = np.nan
        self.array = pd.array(data, dtype="Int64")