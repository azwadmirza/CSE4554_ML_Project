    def cummax(self, axis=0, **kwargs):
        """Cumulative max for each group"""
        if axis != 0:
            return self.apply(lambda x: np.maximum.accumulate(x, axis))

        return self._cython_transform('cummax', numeric_only=False)