    def use(self, styles):
        """
        Set the styles on the current Styler, possibly using styles
        from ``Styler.export``.

        .. versionadded:: 0.17.1

        Parameters
        ----------
        styles: list
            list of style functions

        Returns
        -------
        self : Styler

        See Also
        --------
        Styler.export
        """
        self._todo.extend(styles)
        return self