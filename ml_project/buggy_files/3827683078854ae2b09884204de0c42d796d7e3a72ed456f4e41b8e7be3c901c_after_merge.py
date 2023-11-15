    def mean(self, axis=None, dtype=None, out=None, keepdims=np._NoValue):
        """
        Returns the average of the array elements along given axis.

        Masked entries are ignored, and result elements which are not
        finite will be masked.

        Refer to `numpy.mean` for full documentation.

        See Also
        --------
        ndarray.mean : corresponding function for ndarrays
        numpy.mean : Equivalent function
        numpy.ma.average: Weighted average.

        Examples
        --------
        >>> a = np.ma.array([1,2,3], mask=[False, False, True])
        >>> a
        masked_array(data = [1 2 --],
                     mask = [False False  True],
               fill_value = 999999)
        >>> a.mean()
        1.5

        """
        kwargs = {} if keepdims is np._NoValue else {'keepdims': keepdims}

        if self._mask is nomask:
            result = super(MaskedArray, self).mean(axis=axis,
                                                   dtype=dtype, **kwargs)[()]
        else:
            dsum = self.sum(axis=axis, dtype=dtype, **kwargs)
            cnt = self.count(axis=axis, **kwargs)
            if cnt.shape == () and (cnt == 0):
                result = masked
            else:
                result = dsum * 1. / cnt
        if out is not None:
            out.flat = result
            if isinstance(out, MaskedArray):
                outmask = getattr(out, '_mask', nomask)
                if (outmask is nomask):
                    outmask = out._mask = make_mask_none(out.shape)
                outmask.flat = getattr(result, '_mask', nomask)
            return out
        return result