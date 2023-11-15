    def _sanitize_column(self, key, value):
        # Need to make sure new columns (which go into the BlockManager as new
        # blocks) are always copied

        def reindexer(value):
            # reindex if necessary

            if value.index.equals(self.index) or not len(self.index):
                value = value._values.copy()
            else:

                # GH 4107
                try:
                    value = value.reindex(self.index).values
                except Exception as e:

                    # duplicate axis
                    if not value.index.is_unique:
                        raise e

                    # other
                    raise TypeError('incompatible index of inserted column '
                                    'with frame index')
            return value

        if isinstance(value, Series):
            value = reindexer(value)

        elif isinstance(value, DataFrame):
            # align right-hand-side columns if self.columns
            # is multi-index and self[key] is a sub-frame
            if isinstance(self.columns, MultiIndex) and key in self.columns:
                loc = self.columns.get_loc(key)
                if isinstance(loc, (slice, Series, np.ndarray, Index)):
                    cols = maybe_droplevels(self.columns[loc], key)
                    if len(cols) and not cols.equals(value.columns):
                        value = value.reindex_axis(cols, axis=1)
            # now align rows
            value = reindexer(value).T

        elif isinstance(value, Categorical):
            value = value.copy()

        elif isinstance(value, Index) or is_sequence(value):
            from pandas.core.series import _sanitize_index

            # turn me into an ndarray
            value = _sanitize_index(value, self.index, copy=False)
            if not isinstance(value, (np.ndarray, Index)):
                if isinstance(value, list) and len(value) > 0:
                    value = com._possibly_convert_platform(value)
                else:
                    value = com._asarray_tuplesafe(value)
            elif value.ndim == 2:
                value = value.copy().T
            else:
                value = value.copy()

            # possibly infer to datetimelike
            if is_object_dtype(value.dtype):
                value = _possibly_infer_to_datetimelike(value)

        else:
            # upcast the scalar
            dtype, value = _infer_dtype_from_scalar(value)
            value = np.repeat(value, len(self.index)).astype(dtype)
            value = com._possibly_cast_to_datetime(value, dtype)

        # return internal types directly
        if is_extension_type(value):
            return value

        # broadcast across multiple columns if necessary
        if key in self.columns and value.ndim == 1:
            if (not self.columns.is_unique or
                    isinstance(self.columns, MultiIndex)):
                existing_piece = self[key]
                if isinstance(existing_piece, DataFrame):
                    value = np.tile(value, (len(existing_piece.columns), 1))

        return np.atleast_2d(np.asarray(value))