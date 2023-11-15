    def init_params(self):
        self.v = int_value(self.param.get('V', 0))
        self.r = int_value(self.param['R'])
        self.p = uint_value(self.param['P'], 32)
        self.o = str_value(self.param['O'])
        self.u = str_value(self.param['U'])
        self.length = int_value(self.param.get('Length', 40))
        return