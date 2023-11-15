    def angle(x1, x2):
        xx = np.arccos(np.clip((x1 * x2).sum(axis=0), -1, 1))
        return np.nan_to_num(xx)