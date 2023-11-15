    def drop(self, labels=None, axis=0, index=None, columns=None, level=None,
             inplace=False, errors='raise'):
        """
        Return new object with labels in requested axis removed.

        Parameters
        ----------
        labels : single label or list-like
            Index or column labels to drop.
        axis : int or axis name
            Whether to drop labels from the index (0 / 'index') or
            columns (1 / 'columns').
        index, columns : single label or list-like
            Alternative to specifying `axis` (``labels, axis=1`` is
            equivalent to ``columns=labels``).

            .. versionadded:: 0.21.0
        level : int or level name, default None
            For MultiIndex
        inplace : bool, default False
            If True, do operation inplace and return None.
        errors : {'ignore', 'raise'}, default 'raise'
            If 'ignore', suppress error and existing labels are dropped.

        Returns
        -------
        dropped : type of caller

        Examples
        --------
        >>> df = pd.DataFrame(np.arange(12).reshape(3,4),
                              columns=['A', 'B', 'C', 'D'])
        >>> df
           A  B   C   D
        0  0  1   2   3
        1  4  5   6   7
        2  8  9  10  11

        Drop columns

        >>> df.drop(['B', 'C'], axis=1)
           A   D
        0  0   3
        1  4   7
        2  8  11

        >>> df.drop(columns=['B', 'C'])
           A   D
        0  0   3
        1  4   7
        2  8  11

        Drop a row by index

        >>> df.drop([0, 1])
           A  B   C   D
        2  8  9  10  11

        Notes
        -----
        Specifying both `labels` and `index` or `columns` will raise a
        ValueError.

        """
        inplace = validate_bool_kwarg(inplace, 'inplace')

        if labels is not None:
            if index is not None or columns is not None:
                raise ValueError("Cannot specify both 'labels' and "
                                 "'index'/'columns'")
            axis_name = self._get_axis_name(axis)
            axes = {axis_name: labels}
        elif index is not None or columns is not None:
            axes, _ = self._construct_axes_from_arguments((index, columns), {})
        else:
            raise ValueError("Need to specify at least one of 'labels', "
                             "'index' or 'columns'")

        obj = self

        for axis, labels in axes.items():
            if labels is not None:
                obj = obj._drop_axis(labels, axis, level=level, errors=errors)

        if inplace:
            self._update_inplace(obj)
        else:
            return obj