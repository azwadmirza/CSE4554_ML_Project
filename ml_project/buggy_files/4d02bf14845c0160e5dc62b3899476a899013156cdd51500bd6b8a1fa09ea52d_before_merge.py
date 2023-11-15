    def highlight_null(self, null_color='red'):
        """
        Shade the background ``null_color`` for missing values.

        .. versionadded:: 0.17.1

        Parameters
        ----------
        null_color: str

        Returns
        -------
        self
        """
        self.applymap(self._highlight_null, null_color=null_color)
        return self