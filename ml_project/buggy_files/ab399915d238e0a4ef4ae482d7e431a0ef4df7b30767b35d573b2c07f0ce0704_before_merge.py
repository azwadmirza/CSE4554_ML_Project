    def forward_val(self, y, point=None):
        y[self.diag_idxs] = np.log(y[self.diag_idxs])
        return y