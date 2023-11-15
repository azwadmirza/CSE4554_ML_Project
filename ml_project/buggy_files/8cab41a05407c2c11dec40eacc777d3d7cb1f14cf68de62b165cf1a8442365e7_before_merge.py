    def _simple_new(cls, values, name=None, freq=None, dtype=_TD_DTYPE):
        # `dtype` is passed by _shallow_copy in corner cases, should always
        #  be timedelta64[ns] if present
        if not isinstance(values, TimedeltaArray):
            values = TimedeltaArray._simple_new(values, dtype=dtype, freq=freq)
        else:
            if freq is None:
                freq = values.freq
        assert isinstance(values, TimedeltaArray), type(values)
        assert dtype == _TD_DTYPE, dtype
        assert values.dtype == "m8[ns]", values.dtype

        tdarr = TimedeltaArray._simple_new(values._data, freq=freq)
        result = object.__new__(cls)
        result._data = tdarr
        result.name = name
        # For groupby perf. See note in indexes/base about _index_data
        result._index_data = tdarr._data

        result._reset_identity()
        return result