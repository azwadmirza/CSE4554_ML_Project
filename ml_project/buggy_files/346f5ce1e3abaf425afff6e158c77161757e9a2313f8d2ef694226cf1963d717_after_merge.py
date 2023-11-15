    def to_numpy(self, dtype=None, copy=False, na_value=lib.no_default):
        if self._use_arrow:
            s = self._arrow_array.to_pandas()
        else:
            s = pd.Series(self._ndarray)
        s = s.map(lambda x: x.tolist() if hasattr(x, 'tolist') else x)
        if copy or na_value is not lib.no_default:
            s = s.copy()
        if na_value is not lib.no_default:
            s[self.isna()] = na_value
        return np.asarray(s)