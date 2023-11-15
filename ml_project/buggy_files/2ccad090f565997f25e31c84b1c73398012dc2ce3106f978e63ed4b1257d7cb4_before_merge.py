    def __getitem__(self, indx):
        """
        x.__getitem__(y) <==> x[y]

        Return the item described by i, as a masked array.

        """
        dout = self.data[indx]
        # We could directly use ndarray.__getitem__ on self.
        # But then we would have to modify __array_finalize__ to prevent the
        # mask of being reshaped if it hasn't been set up properly yet
        # So it's easier to stick to the current version
        _mask = self._mask
        # Did we extract a single item?
        if not getattr(dout, 'ndim', False):
            # A record
            if isinstance(dout, np.void):
                mask = _mask[indx]
                # We should always re-cast to mvoid, otherwise users can
                # change masks on rows that already have masked values, but not
                # on rows that have no masked values, which is inconsistent.
                dout = mvoid(dout, mask=mask, hardmask=self._hardmask)
            # Just a scalar
            elif _mask is not nomask and _mask[indx]:
                return masked
        elif self.dtype.type is np.object_ and self.dtype is not dout.dtype:
            # self contains an object array of arrays (yes, that happens).
            # If masked, turn into a MaskedArray, with everything masked.
            if _mask is not nomask and _mask[indx]:
                return MaskedArray(dout, mask=True)
        else:
            # Force dout to MA
            dout = dout.view(type(self))
            # Inherit attributes from self
            dout._update_from(self)
            # Check the fill_value
            if isinstance(indx, basestring):
                if self._fill_value is not None:
                    dout._fill_value = self._fill_value[indx]
                dout._isfield = True
            # Update the mask if needed
            if _mask is not nomask:
                dout._mask = _mask[indx]
                # set shape to match that of data; this is needed for matrices
                dout._mask.shape = dout.shape
                dout._sharedmask = True
                # Note: Don't try to check for m.any(), that'll take too long
        return dout