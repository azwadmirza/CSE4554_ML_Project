    def mean(self, axis=None, skipna=None, level=None, numeric_only=None, **kwargs):
        return self._stat_operation("mean", axis, skipna, level, numeric_only, **kwargs)