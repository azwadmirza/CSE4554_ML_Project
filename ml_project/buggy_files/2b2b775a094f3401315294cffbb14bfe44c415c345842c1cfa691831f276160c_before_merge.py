    def sel(self, method=None, tolerance=None, drop=False, **indexers):
        """Returns a new dataset with each array indexed by tick labels
        along the specified dimension(s).

        In contrast to `Dataset.isel`, indexers for this method should use
        labels instead of integers.

        Under the hood, this method is powered by using pandas's powerful Index
        objects. This makes label based indexing essentially just as fast as
        using integer indexing.

        It also means this method uses pandas's (well documented) logic for
        indexing. This means you can use string shortcuts for datetime indexes
        (e.g., '2000-01' to select all values in January 2000). It also means
        that slices are treated as inclusive of both the start and stop values,
        unlike normal Python indexing.

        Parameters
        ----------
        method : {None, 'nearest', 'pad'/'ffill', 'backfill'/'bfill'}, optional
            Method to use for inexact matches (requires pandas>=0.16):

            * None (default): only exact matches
            * pad / ffill: propagate last valid index value forward
            * backfill / bfill: propagate next valid index value backward
            * nearest: use nearest valid index value
        tolerance : optional
            Maximum distance between original and new labels for inexact
            matches. The values of the index at the matching locations most
            satisfy the equation ``abs(index[indexer] - target) <= tolerance``.
            Requires pandas>=0.17.
        drop : bool, optional
            If ``drop=True``, drop coordinates variables in `indexers` instead
            of making them scalar.
        **indexers : {dim: indexer, ...}
            Keyword arguments with names matching dimensions and values given
            by scalars, slices or arrays of tick labels. For dimensions with
            multi-index, the indexer may also be a dict-like object with keys
            matching index level names.
            If DataArrays are passed as indexers, xarray-style indexing will be
            carried out. See :ref:`indexing` for the details.

        Returns
        -------
        obj : Dataset
            A new Dataset with the same contents as this dataset, except each
            variable and dimension is indexed by the appropriate indexers.
            If indexer DataArrays have coordinates that do not conflict with
            this object, then these coordinates will be attached.
            In general, each array's data will be a view of the array's data
            in this dataset, unless vectorized indexing was triggered by using
            an array indexer, in which case the data will be a copy.


        See Also
        --------
        Dataset.isel
        DataArray.sel
        """
        from .dataarray import DataArray

        v_indexers = {k: v.variable.data if isinstance(v, DataArray) else v
                      for k, v in indexers.items()}

        pos_indexers, new_indexes = indexing.remap_label_indexers(
            self, v_indexers, method=method, tolerance=tolerance
        )
        # attach indexer's coordinate to pos_indexers
        for k, v in indexers.items():
            if isinstance(v, Variable):
                pos_indexers[k] = Variable(v.dims, pos_indexers[k])
            elif isinstance(v, DataArray):
                # drop coordinates found in indexers since .sel() already
                # ensures alignments
                coords = OrderedDict((k, v) for k, v in v._coords.items()
                                     if k not in indexers)
                pos_indexers[k] = DataArray(pos_indexers[k],
                                            coords=coords, dims=v.dims)
        result = self.isel(drop=drop, **pos_indexers)
        return result._replace_indexes(new_indexes)