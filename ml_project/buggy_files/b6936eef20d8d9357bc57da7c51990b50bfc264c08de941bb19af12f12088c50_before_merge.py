    def background_gradient(self, cmap='PuBu', low=0, high=0, axis=0,
                            subset=None):
        """
        Color the background in a gradient according to
        the data in each column (optionally row).
        Requires matplotlib.

        .. versionadded:: 0.17.1

        Parameters
        ----------
        cmap: str or colormap
            matplotlib colormap
        low, high: float
            compress the range by these values.
        axis: int or str
            1 or 'columns' for colunwise, 0 or 'index' for rowwise
        subset: IndexSlice
            a valid slice for ``data`` to limit the style application to

        Returns
        -------
        self

        Notes
        -----
        Tune ``low`` and ``high`` to keep the text legible by
        not using the entire range of the color map. These extend
        the range of the data by ``low * (x.max() - x.min())``
        and ``high * (x.max() - x.min())`` before normalizing.
        """
        subset = _maybe_numeric_slice(self.data, subset)
        subset = _non_reducing_slice(subset)
        self.apply(self._background_gradient, cmap=cmap, subset=subset,
                   axis=axis, low=low, high=high)
        return self