    def to_numpy(self, dtype=None, copy=False, na_value=lib.no_default):
        s = self._arrow_array.to_pandas().map(
            lambda x: x.tolist() if x is not None else x)
        if copy or na_value is not lib.no_default:
            s = s.copy()
        if na_value is not lib.no_default:
            s[self.isna()] = na_value
        return np.asarray(s)