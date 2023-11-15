    def calc_num_bins(self, values):
        """Calculate optimal number of bins using IQR.

        From: http://stats.stackexchange.com/questions/114490/optimal-bin-width-for-two-dimensional-histogram

        """
        iqr = self.q3.value - self.q1.value

        if iqr == 0:
            self.bin_width = np.sqrt(values.size)
        else:
            self.bin_width = 2 * iqr * (len(values) ** -(1. / 3.))

        self.bin_count = int(np.ceil((values.max() - values.min()) / self.bin_width))

        if self.bin_count == 1:
            self.bin_count = 3