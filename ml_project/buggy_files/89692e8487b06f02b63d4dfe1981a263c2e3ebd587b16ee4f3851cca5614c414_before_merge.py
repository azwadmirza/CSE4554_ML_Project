    def astype(self, dtype, casting="unsafe", copy=True, keep_attrs=True):
        """
        Copy of the Variable object, with data cast to a specified type.

        Parameters
        ----------
        dtype : str or dtype
             Typecode or data-type to which the array is cast.
        casting : {'no', 'equiv', 'safe', 'same_kind', 'unsafe'}, optional
             Controls what kind of data casting may occur. Defaults to 'unsafe'
             for backwards compatibility.

             * 'no' means the data types should not be cast at all.
             * 'equiv' means only byte-order changes are allowed.
             * 'safe' means only casts which can preserve values are allowed.
             * 'same_kind' means only safe casts or casts within a kind,
                 like float64 to float32, are allowed.
             * 'unsafe' means any data conversions may be done.
        copy : bool, optional
             By default, astype always returns a newly allocated array. If this
             is set to False and the `dtype` requirement is satisfied, the input
             array is returned instead of a copy.
        keep_attrs : bool, optional
            By default, astype keeps attributes. Set to False to remove
            attributes in the returned object.

        Returns
        -------
        out : same as object
            New object with data cast to the specified type.

        See also
        --------
        np.ndarray.astype
        dask.array.Array.astype
        """
        from .computation import apply_ufunc

        return apply_ufunc(
            duck_array_ops.astype,
            self,
            kwargs=dict(dtype=dtype, casting=casting, copy=copy),
            keep_attrs=keep_attrs,
            dask="allowed",
        )