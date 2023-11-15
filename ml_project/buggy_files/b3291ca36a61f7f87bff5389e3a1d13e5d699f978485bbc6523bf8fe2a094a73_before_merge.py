    def _simple_new(cls, values, name=None, freq=None, **kwargs):
        """
        Create a new PeriodIndex.

        Parameters
        ----------
        values : PeriodArray, PeriodIndex, Index[int64], ndarray[int64]
            Values that can be converted to a PeriodArray without inference
            or coercion.

        """
        # TODO: raising on floats is tested, but maybe not useful.
        # Should the callers know not to pass floats?
        # At the very least, I think we can ensure that lists aren't passed.
        if isinstance(values, list):
            values = np.asarray(values)
        if is_float_dtype(values):
            raise TypeError("PeriodIndex._simple_new does not accept floats.")
        values = PeriodArray(values, freq=freq)

        if not isinstance(values, PeriodArray):
            raise TypeError("PeriodIndex._simple_new only accepts PeriodArray")
        result = object.__new__(cls)
        result._data = values
        result.name = name
        result._reset_identity()
        return result