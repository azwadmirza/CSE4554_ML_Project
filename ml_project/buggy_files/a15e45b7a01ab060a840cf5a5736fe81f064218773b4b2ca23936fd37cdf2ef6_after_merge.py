    def var(self, axis=None, dtype=None, out=None, ddof=0,
            keepdims=np._NoValue):
        """
        Returns the variance of the array elements along given axis.

        Masked entries are ignored, and result elements which are not
        finite will be masked.

        Refer to `numpy.var` for full documentation.

        See Also
        --------
        ndarray.var : corresponding function for ndarrays
        numpy.var : Equivalent function
        """
        kwargs = {} if keepdims is np._NoValue else {'keepdims': keepdims}

        # Easy case: nomask, business as usual
        if self._mask is nomask:
            ret = super(MaskedArray, self).var(axis=axis, dtype=dtype, out=out,
                                               ddof=ddof, **kwargs)[()]
            if out is not None:
                if isinstance(out, MaskedArray):
                    out.__setmask__(nomask)
                return out
            return ret

        # Some data are masked, yay!
        cnt = self.count(axis=axis, **kwargs) - ddof
        danom = self - self.mean(axis, dtype, keepdims=True)
        if iscomplexobj(self):
            danom = umath.absolute(danom) ** 2
        else:
            danom *= danom
        dvar = divide(danom.sum(axis, **kwargs), cnt).view(type(self))
        # Apply the mask if it's not a scalar
        if dvar.ndim:
            dvar._mask = mask_or(self._mask.all(axis, **kwargs), (cnt <= 0))
            dvar._update_from(self)
        elif getattr(dvar, '_mask', False):
            # Make sure that masked is returned when the scalar is masked.
            dvar = masked
            if out is not None:
                if isinstance(out, MaskedArray):
                    out.flat = 0
                    out.__setmask__(True)
                elif out.dtype.kind in 'biu':
                    errmsg = "Masked data information would be lost in one or "\
                             "more location."
                    raise MaskError(errmsg)
                else:
                    out.flat = np.nan
                return out
        # In case with have an explicit output
        if out is not None:
            # Set the data
            out.flat = dvar
            # Set the mask if needed
            if isinstance(out, MaskedArray):
                out.__setmask__(dvar.mask)
            return out
        return dvar