    def applymap(self, func, subset=None, **kwargs):
        """
        Apply a function elementwise, updating the HTML
        representation with the result.

        .. versionadded:: 0.17.1

        Parameters
        ----------
        func : function
        subset : IndexSlice
            a valid indexer to limit ``data`` to *before* applying the
            function. Consider using a pandas.IndexSlice
        kwargs : dict
            pass along to ``func``

        Returns
        -------
        self : Styler

        """
        self._todo.append((lambda instance: getattr(instance, '_applymap'),
                           (func, subset), kwargs))
        return self