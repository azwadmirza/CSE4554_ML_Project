    def resample(self, freq, dim, how='mean', skipna=None, closed=None,
                 label=None, base=0, keep_attrs=False):
        """Resample this object to a new temporal resolution.

        Handles both downsampling and upsampling. Upsampling with filling is
        not yet supported; if any intervals contain no values in the original
        object, they will be given the value ``NaN``.

        Parameters
        ----------
        freq : str
            String in the '#offset' to specify the step-size along the
            resampled dimension, where '#' is an (optional) integer multipler
            (default 1) and 'offset' is any pandas date offset alias. Examples
            of valid offsets include:

            * 'AS': year start
            * 'QS-DEC': quarterly, starting on December 1
            * 'MS': month start
            * 'D': day
            * 'H': hour
            * 'Min': minute

            The full list of these offset aliases is documented in pandas [1]_.
        dim : str
            Name of the dimension to resample along (e.g., 'time').
        how : str or func, optional
            Used for downsampling. If a string, ``how`` must be a valid
            aggregation operation supported by xarray. Otherwise, ``how`` must be
            a function that can be called like ``how(values, axis)`` to reduce
            ndarray values along the given axis. Valid choices that can be
            provided as a string include all the usual Dataset/DataArray
            aggregations (``all``, ``any``, ``argmax``, ``argmin``, ``max``,
            ``mean``, ``median``, ``min``, ``prod``, ``sum``, ``std`` and
            ``var``), as well as ``first`` and ``last``.
        skipna : bool, optional
            Whether to skip missing values when aggregating in downsampling.
        closed : 'left' or 'right', optional
            Side of each interval to treat as closed.
        label : 'left or 'right', optional
            Side of each interval to use for labeling.
        base : int, optionalt
            For frequencies that evenly subdivide 1 day, the "origin" of the
            aggregated intervals. For example, for '24H' frequency, base could
            range from 0 through 23.
        keep_attrs : bool, optional
            If True, the object's attributes (`attrs`) will be copied from
            the original object to the new one.  If False (default), the new
            object will be returned without attributes.

        Returns
        -------
        resampled : same type as caller
            This object resampled.

        References
        ----------

        .. [1] http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
        """
        from .dataarray import DataArray

        RESAMPLE_DIM = '__resample_dim__'
        if isinstance(dim, basestring):
            dim = self[dim]
        group = DataArray(dim, [(RESAMPLE_DIM, dim)], name=RESAMPLE_DIM)
        time_grouper = pd.TimeGrouper(freq=freq, how=how, closed=closed,
                                      label=label, base=base)
        gb = self.groupby_cls(self, group, grouper=time_grouper)
        if isinstance(how, basestring):
            f = getattr(gb, how)
            if how in ['first', 'last']:
                result = f(skipna=skipna, keep_attrs=keep_attrs)
            else:
                result = f(dim=dim.name, skipna=skipna, keep_attrs=keep_attrs)
        else:
            result = gb.reduce(how, dim=dim.name, keep_attrs=keep_attrs)
        result = result.rename({RESAMPLE_DIM: dim.name})
        return result