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