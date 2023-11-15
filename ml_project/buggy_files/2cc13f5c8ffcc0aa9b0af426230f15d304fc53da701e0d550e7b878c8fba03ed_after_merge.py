    def astype(self, dtype, copy=True):
        # Some notes on cases we don't have to handle here in the base class:
        #   1. PeriodArray.astype handles period -> period
        #   2. DatetimeArray.astype handles conversion between tz.
        #   3. DatetimeArray.astype handles datetime -> period
        dtype = pandas_dtype(dtype)

        if is_object_dtype(dtype):
            return self._box_values(self.asi8.ravel()).reshape(self.shape)
        elif is_string_dtype(dtype) and not is_categorical_dtype(dtype):
            if is_extension_array_dtype(dtype):
                arr_cls = dtype.construct_array_type()
                return arr_cls._from_sequence(self, dtype=dtype, copy=copy)
            else:
                return self._format_native_types()
        elif is_integer_dtype(dtype):
            # we deliberately ignore int32 vs. int64 here.
            # See https://github.com/pandas-dev/pandas/issues/24381 for more.
            warnings.warn(
                f"casting {self.dtype} values to int64 with .astype(...) is "
                "deprecated and will raise in a future version. "
                "Use .view(...) instead.",
                FutureWarning,
                stacklevel=3,
            )

            values = self.asi8

            if is_unsigned_integer_dtype(dtype):
                # Again, we ignore int32 vs. int64
                values = values.view("uint64")

            if copy:
                values = values.copy()
            return values
        elif (
            is_datetime_or_timedelta_dtype(dtype)
            and not is_dtype_equal(self.dtype, dtype)
        ) or is_float_dtype(dtype):
            # disallow conversion between datetime/timedelta,
            # and conversions for any datetimelike to float
            msg = f"Cannot cast {type(self).__name__} to dtype {dtype}"
            raise TypeError(msg)
        elif is_categorical_dtype(dtype):
            arr_cls = dtype.construct_array_type()
            return arr_cls(self, dtype=dtype)
        else:
            return np.asarray(self, dtype=dtype)