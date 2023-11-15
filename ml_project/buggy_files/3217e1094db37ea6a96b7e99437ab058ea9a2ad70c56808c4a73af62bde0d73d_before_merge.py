    def apply(self, func, axis=0, subset=None, **kwargs):
        """
        Apply a function column-wise, row-wise, or table-wase,
        updating the HTML representation with the result.

        .. versionadded:: 0.17.1

        Parameters
        ----------
        func: function
        axis: int, str or None
            apply to each column (``axis=0`` or ``'index'``)
            or to each row (``axis=1`` or ``'columns'``) or
            to the entire DataFrame at once with ``axis=None``.
        subset: IndexSlice
            a valid indexer to limit ``data`` to *before* applying the
            function. Consider using a pandas.IndexSlice
        kwargs: dict
            pass along to ``func``

        Returns
        -------
        self

        Notes
        -----
        This is similar to ``DataFrame.apply``, except that ``axis=None``
        applies the function to the entire DataFrame at once,
        rather than column-wise or row-wise.
        """
        self._todo.append((lambda instance: getattr(instance, '_apply'),
                           (func, axis, subset), kwargs))
        return self