    def calc_real_time(self):
        """calculate and return real time for whole hypermap
        in seconds
        """
        line_cnt_sum = np.sum(self.line_counter, dtype=np.float64)
        line_avg = self.dsp_metadata['LineAverage']
        pix_avg = self.dsp_metadata['PixelAverage']
        pix_time = self.dsp_metadata['PixelTime']
        width = self.image.width
        real_time = line_cnt_sum * line_avg * pix_avg * pix_time * width * 1E-6
        return float(real_time)