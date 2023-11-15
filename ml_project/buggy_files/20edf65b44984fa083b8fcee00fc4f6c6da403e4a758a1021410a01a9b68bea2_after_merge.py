    def _cython_operation(self, kind, values, how, axis):
        assert kind in ['transform', 'aggregate']

        # can we do this operation with our cython functions
        # if not raise NotImplementedError

        # we raise NotImplemented if this is an invalid operation
        # entirely, e.g. adding datetimes

        # categoricals are only 1d, so we
        # are not setup for dim transforming
        if is_categorical_dtype(values):
            raise NotImplementedError(
                "categoricals are not support in cython ops ATM")
        elif is_datetime64_any_dtype(values):
            if how in ['add', 'prod', 'cumsum', 'cumprod']:
                raise NotImplementedError(
                    "datetime64 type does not support {} "
                    "operations".format(how))
        elif is_timedelta64_dtype(values):
            if how in ['prod', 'cumprod']:
                raise NotImplementedError(
                    "timedelta64 type does not support {} "
                    "operations".format(how))

        arity = self._cython_arity.get(how, 1)

        vdim = values.ndim
        swapped = False
        if vdim == 1:
            values = values[:, None]
            out_shape = (self.ngroups, arity)
        else:
            if axis > 0:
                swapped = True
                values = values.swapaxes(0, axis)
            if arity > 1:
                raise NotImplementedError("arity of more than 1 is not "
                                          "supported for the 'how' argument")
            out_shape = (self.ngroups,) + values.shape[1:]

        is_datetimelike = needs_i8_conversion(values.dtype)
        is_numeric = is_numeric_dtype(values.dtype)

        if is_datetimelike:
            values = values.view('int64')
            is_numeric = True
        elif is_bool_dtype(values.dtype):
            values = _ensure_float64(values)
        elif is_integer_dtype(values):
            # we use iNaT for the missing value on ints
            # so pre-convert to guard this condition
            if (values == tslib.iNaT).any():
                values = _ensure_float64(values)
            else:
                values = values.astype('int64', copy=False)
        elif is_numeric and not is_complex_dtype(values):
            values = _ensure_float64(values)
        else:
            values = values.astype(object)

        try:
            func, dtype_str = self._get_cython_function(
                kind, how, values, is_numeric)
        except NotImplementedError:
            if is_numeric:
                values = _ensure_float64(values)
                func, dtype_str = self._get_cython_function(
                    kind, how, values, is_numeric)
            else:
                raise

        if is_numeric:
            out_dtype = '%s%d' % (values.dtype.kind, values.dtype.itemsize)
        else:
            out_dtype = 'object'

        labels, _, _ = self.group_info

        if kind == 'aggregate':
            result = _maybe_fill(np.empty(out_shape, dtype=out_dtype),
                                 fill_value=np.nan)
            counts = np.zeros(self.ngroups, dtype=np.int64)
            result = self._aggregate(
                result, counts, values, labels, func, is_numeric,
                is_datetimelike)
        elif kind == 'transform':
            result = _maybe_fill(np.empty_like(values, dtype=out_dtype),
                                 fill_value=np.nan)

            result = self._transform(
                result, values, labels, func, is_numeric, is_datetimelike)

        if is_integer_dtype(result):
            mask = result == tslib.iNaT
            if mask.any():
                result = result.astype('float64')
                result[mask] = np.nan

        if kind == 'aggregate' and \
           self._filter_empty_groups and not counts.all():
            if result.ndim == 2:
                try:
                    result = lib.row_bool_subset(
                        result, (counts > 0).view(np.uint8))
                except ValueError:
                    result = lib.row_bool_subset_object(
                        _ensure_object(result),
                        (counts > 0).view(np.uint8))
            else:
                result = result[counts > 0]

        if vdim == 1 and arity == 1:
            result = result[:, 0]

        if how in self._name_functions:
            # TODO
            names = self._name_functions[how]()
        else:
            names = None

        if swapped:
            result = result.swapaxes(0, axis)

        return result, names