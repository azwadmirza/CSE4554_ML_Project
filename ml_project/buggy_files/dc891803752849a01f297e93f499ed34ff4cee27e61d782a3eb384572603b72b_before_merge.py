    def angle(x1, x2):
        xx = np.arccos((x1 * x2).sum(axis=0))
        xx[np.isnan(xx)] = 0
        return xx