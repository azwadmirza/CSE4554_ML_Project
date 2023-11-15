def _bool_method_SERIES(cls, op, special):
    """
    Wrapper function for Series arithmetic operations, to avoid
    code duplication.
    """

    def na_op(x, y):
        try:
            result = op(x, y)
        except TypeError:
            if isinstance(y, list):
                y = construct_1d_object_array_from_listlike(y)

            if isinstance(y, (np.ndarray, ABCSeries, ABCIndexClass)):
                if (is_bool_dtype(x.dtype) and is_bool_dtype(y.dtype)):
                    result = op(x, y)  # when would this be hit?
                else:
                    x = ensure_object(x)
                    y = ensure_object(y)
                    result = libops.vec_binop(x, y, op)
            else:
                # let null fall thru
                if not isna(y):
                    y = bool(y)
                try:
                    result = libops.scalar_binop(x, y, op)
                except:
                    raise TypeError("cannot compare a dtyped [{dtype}] array "
                                    "with a scalar of type [{typ}]"
                                    .format(dtype=x.dtype,
                                            typ=type(y).__name__))

        return result

    fill_int = lambda x: x.fillna(0)
    fill_bool = lambda x: x.fillna(False).astype(bool)

    def wrapper(self, other):
        is_self_int_dtype = is_integer_dtype(self.dtype)

        self, other = _align_method_SERIES(self, other, align_asobject=True)

        if isinstance(other, ABCDataFrame):
            # Defer to DataFrame implementation; fail early
            return NotImplemented

        elif isinstance(other, ABCSeries):
            name = get_op_result_name(self, other)
            is_other_int_dtype = is_integer_dtype(other.dtype)
            other = fill_int(other) if is_other_int_dtype else fill_bool(other)

            filler = (fill_int if is_self_int_dtype and is_other_int_dtype
                      else fill_bool)

            res_values = na_op(self.values, other.values)
            unfilled = self._constructor(res_values,
                                         index=self.index, name=name)
            return filler(unfilled)

        else:
            # scalars, list, tuple, np.array
            filler = (fill_int if is_self_int_dtype and
                      is_integer_dtype(np.asarray(other)) else fill_bool)

            res_values = na_op(self.values, other)
            unfilled = self._constructor(res_values, index=self.index)
            return filler(unfilled).__finalize__(self)

    return wrapper