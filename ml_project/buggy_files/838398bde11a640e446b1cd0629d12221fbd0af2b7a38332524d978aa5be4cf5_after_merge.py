    def highlight_min(self, subset=None, color='yellow', axis=0):
        """
        Highlight the minimum by shading the background

        .. versionadded:: 0.17.1

        Parameters
        ----------
        subset: IndexSlice, default None
            a valid slice for ``data`` to limit the style application to
        color: str, default 'yellow'
        axis: int, str, or None; default None
            0 or 'index' for columnwise, 1 or 'columns' for rowwise
            or ``None`` for tablewise (the default)

        Returns
        -------
        self : Styler
        """
        return self._highlight_handler(subset=subset, color=color, axis=axis,
                                       max_=False)