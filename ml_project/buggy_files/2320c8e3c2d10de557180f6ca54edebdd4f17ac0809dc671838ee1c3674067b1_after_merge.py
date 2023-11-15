    def rolling(self, min_periods=None, center=False, **windows):
        """
        Rolling window object.

        Rolling window aggregations are much faster when bottleneck is
        installed.

        Parameters
        ----------
        min_periods : int, default None
            Minimum number of observations in window required to have a value
            (otherwise result is NA). The default, None, is equivalent to
            setting min_periods equal to the size of the window.
        center : boolean, default False
            Set the labels at the center of the window.
        **windows : dim=window
            dim : str
                Name of the dimension to create the rolling iterator
                along (e.g., `time`).
            window : int
                Size of the moving window.

        Returns
        -------
        rolling : type of input argument
        """

        return self._rolling_cls(self, min_periods=min_periods,
                                 center=center, **windows)