def _arith_method_SERIES(cls, op, special):
    """
    Wrapper function for Series arithmetic operations, to avoid
    code duplication.
    """
    str_rep = _get_opstr(op, cls)
    op_name = _get_op_name(op, special)
    eval_kwargs = _gen_eval_kwargs(op_name)
    fill_zeros = _gen_fill_zeros(op_name)
    construct_result = (_construct_divmod_result
                        if op in [divmod, rdivmod] else _construct_result)

    def na_op(x, y):
        import pandas.core.computation.expressions as expressions
        try:
            result = expressions.evaluate(op, str_rep, x, y, **eval_kwargs)
        except TypeError:
            result = masked_arith_op(x, y, op)

        result = missing.fill_zeros(result, x, y, op_name, fill_zeros)
        return result

    def safe_na_op(lvalues, rvalues):
        """
        return the result of evaluating na_op on the passed in values

        try coercion to object type if the native types are not compatible

        Parameters
        ----------
        lvalues : array-like
        rvalues : array-like

        Raises
        ------
        TypeError: invalid operation
        """
        try:
            with np.errstate(all='ignore'):
                return na_op(lvalues, rvalues)
        except Exception:
            if is_object_dtype(lvalues):
                return libalgos.arrmap_object(lvalues,
                                              lambda x: op(x, rvalues))
            raise

    def wrapper(left, right):
        if isinstance(right, ABCDataFrame):
            return NotImplemented

        left, right = _align_method_SERIES(left, right)
        res_name = get_op_result_name(left, right)
        right = maybe_upcast_for_op(right)

        if is_categorical_dtype(left):
            raise TypeError("{typ} cannot perform the operation "
                            "{op}".format(typ=type(left).__name__, op=str_rep))

        elif (is_extension_array_dtype(left) or
                (is_extension_array_dtype(right) and not is_scalar(right))):
            # GH#22378 disallow scalar to exclude e.g. "category", "Int64"
            return dispatch_to_extension_op(op, left, right)

        elif is_datetime64_dtype(left) or is_datetime64tz_dtype(left):
            result = dispatch_to_index_op(op, left, right, pd.DatetimeIndex)
            return construct_result(left, result,
                                    index=left.index, name=res_name,
                                    dtype=result.dtype)

        elif is_timedelta64_dtype(left):
            result = dispatch_to_index_op(op, left, right, pd.TimedeltaIndex)
            return construct_result(left, result,
                                    index=left.index, name=res_name)

        elif is_timedelta64_dtype(right):
            # We should only get here with non-scalar or timedelta64('NaT')
            #  values for right
            # Note: we cannot use dispatch_to_index_op because
            #  that may incorrectly raise TypeError when we
            #  should get NullFrequencyError
            result = op(pd.Index(left), right)
            return construct_result(left, result,
                                    index=left.index, name=res_name,
                                    dtype=result.dtype)

        lvalues = left.values
        rvalues = right
        if isinstance(rvalues, ABCSeries):
            rvalues = rvalues.values

        result = safe_na_op(lvalues, rvalues)
        return construct_result(left, result,
                                index=left.index, name=res_name, dtype=None)

    wrapper.__name__ = op_name
    return wrapper