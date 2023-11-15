    def __getitem__(self, indx):
        """
        x.__getitem__(y) <==> x[y]

        Return the item described by i, as a masked array.

        """
        # We could directly use ndarray.__getitem__ on self.
        # But then we would have to modify __array_finalize__ to prevent the
        # mask of being reshaped if it hasn't been set up properly yet
        # So it's easier to stick to the current version
        dout = self.data[indx]
        _mask = self._mask

        def _is_scalar(m):
            return not isinstance(m, np.ndarray)

        def _scalar_heuristic(arr, elem):
            """
            Return whether `elem` is a scalar result of indexing `arr`, or None
            if undecidable without promoting nomask to a full mask
            """
            # obviously a scalar
            if not isinstance(elem, np.ndarray):
                return True

            # object array scalar indexing can return anything
            elif arr.dtype.type is np.object_:
                if arr.dtype is not elem.dtype:
                    # elem is an array, but dtypes do not match, so must be
                    # an element
                    return True

            # well-behaved subclass that only returns 0d arrays when
            # expected - this is not a scalar
            elif type(arr).__getitem__ == ndarray.__getitem__:
                return False

            return None

        if _mask is not nomask:
            # _mask cannot be a subclass, so it tells us whether we should
            # expect a scalar. It also cannot be of dtype object.
            mout = _mask[indx]
            scalar_expected = _is_scalar(mout)

        else:
            # attempt to apply the heuristic to avoid constructing a full mask
            mout = nomask
            scalar_expected = _scalar_heuristic(self.data, dout)
            if scalar_expected is None:
                # heuristics have failed
                # construct a full array, so we can be certain. This is costly.
                # we could also fall back on ndarray.__getitem__(self.data, indx)
                scalar_expected = _is_scalar(getmaskarray(self)[indx])

        # Did we extract a single item?
        if scalar_expected:
            # A record
            if isinstance(dout, np.void):
                # We should always re-cast to mvoid, otherwise users can
                # change masks on rows that already have masked values, but not
                # on rows that have no masked values, which is inconsistent.
                return mvoid(dout, mask=mout, hardmask=self._hardmask)

            # special case introduced in gh-5962
            elif (self.dtype.type is np.object_ and
                  isinstance(dout, np.ndarray) and
                  dout is not masked):
                # If masked, turn into a MaskedArray, with everything masked.
                if mout:
                    return MaskedArray(dout, mask=True)
                else:
                    return dout

            # Just a scalar
            else:
                if mout:
                    return masked
                else:
                    return dout
        else:
            # Force dout to MA
            dout = dout.view(type(self))
            # Inherit attributes from self
            dout._update_from(self)
            # Check the fill_value
            if is_string_or_list_of_strings(indx):
                if self._fill_value is not None:
                    dout._fill_value = self._fill_value[indx]

                    # If we're indexing a multidimensional field in a
                    # structured array (such as dtype("(2,)i2,(2,)i1")),
                    # dimensionality goes up (M[field].ndim == M.ndim +
                    # M.dtype[field].ndim).  That's fine for
                    # M[field] but problematic for M[field].fill_value
                    # which should have shape () to avoid breaking several
                    # methods. There is no great way out, so set to
                    # first element.  See issue #6723.
                    if dout._fill_value.ndim > 0:
                        if not (dout._fill_value ==
                                dout._fill_value.flat[0]).all():
                            warnings.warn(
                                "Upon accessing multidimensional field "
                                f"{indx!s}, need to keep dimensionality "
                                "of fill_value at 0. Discarding "
                                "heterogeneous fill_value and setting "
                                f"all to {dout._fill_value[0]!s}.",
                                stacklevel=2)
                        dout._fill_value = dout._fill_value.flat[0]
                dout._isfield = True
            # Update the mask if needed
            if mout is not nomask:
                # set shape to match that of data; this is needed for matrices
                dout._mask = reshape(mout, dout.shape)
                dout._sharedmask = True
                # Note: Don't try to check for m.any(), that'll take too long
        return dout