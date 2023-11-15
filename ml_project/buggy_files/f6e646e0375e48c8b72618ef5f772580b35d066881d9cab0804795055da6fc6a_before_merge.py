    def reduce(self, func, **kwargs):
        """Reduce the items in this group by applying `func` along some
        dimension(s).

        Parameters
        ----------
        func : function
            Function which can be called in the form
            `func(x, **kwargs)` to return the result of collapsing an
            np.ndarray over an the rolling dimension.
        **kwargs : dict
            Additional keyword arguments passed on to `func`.

        Returns
        -------
        reduced : DataArray
            Array with summarized data.
        """

        windows = [window.reduce(func, dim=self.dim, **kwargs)
                   for _, window in self]

        # Find valid windows based on count
        concat_dim = self.window_labels if self.dim in self.obj else self.dim
        counts = concat([window.count(dim=self.dim) for _, window in self],
                        dim=concat_dim)
        result = concat(windows, dim=concat_dim)
        # restore dim order
        result = result.transpose(*self.obj.dims)

        result = result.where(counts >= self._min_periods)

        if self.center:
            result = self._center_result(result)

        return result