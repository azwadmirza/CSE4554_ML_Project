    def calc_num_bins(self, values):
        iqr = self.q3.value - self.q1.value
        self.bin_width = 2 * iqr * (len(values) ** -(1. / 3.))
        self.bin_count = int(np.ceil((values.max() - values.min())/self.bin_width))