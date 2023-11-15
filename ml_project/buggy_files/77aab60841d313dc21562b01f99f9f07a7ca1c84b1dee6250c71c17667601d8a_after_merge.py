    def setup(self):
        self.rng = date_range(start='1/1/2000', periods=20000, freq='H')
        self.strings = [x.strftime('%Y-%m-%d %H:%M:%S') for x in self.rng]
        self.strings_nosep = [x.strftime('%Y%m%d %H:%M:%S') for x in self.rng]
        self.strings_tz_space = [x.strftime('%Y-%m-%d %H:%M:%S') + ' -0800'
                                 for x in self.rng]