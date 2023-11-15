    def cummin(self, axis=0, **kwargs):
        """Cumulative min for each group"""
        if axis != 0:
            return self.apply(lambda x: np.minimum.accumulate(x, axis))

        return self._cython_transform('cummin', **kwargs)