    def setup(self):
        self.N = 100000
        self.rng = date_range(start='1/1/2000', periods=self.N, freq='T')
        if hasattr(Series, 'convert'):
            Series.resample = Series.convert
        self.ts = Series(np.random.randn(self.N), index=self.rng)
        self.rng = date_range(start='1/1/2000', periods=20000, freq='H')
        self.strings = [x.strftime('%Y-%m-%d %H:%M:%S') for x in self.rng]