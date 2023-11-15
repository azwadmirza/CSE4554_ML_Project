def _install():
    from ..core import DATAFRAME_TYPE, SERIES_TYPE, INDEX_TYPE

    def _register_method(cls, name, func, wrapper=None):
        if wrapper is None:
            @functools.wraps(func)
            def wrapper(df, *args, **kwargs):
                return func(df, *args, **kwargs)

        try:
            if issubclass(cls, DATAFRAME_TYPE):
                wrapper.__doc__ = func.__frame_doc__
            elif issubclass(cls, SERIES_TYPE):
                wrapper.__doc__ = func.__series_doc__
            else:
                wrapper = func
        except AttributeError:
            wrapper = func

        wrapper.__name__ = func.__name__
        setattr(cls, name, wrapper)

    def _register_bin_method(cls, name, func):
        def call_df_fill(df, other, axis='columns', level=None, fill_value=None):
            return func(df, other, axis=axis, level=level, fill_value=fill_value)

        def call_df_no_fill(df, other, axis='columns', level=None):
            return func(df, other, axis=axis, level=level)

        def call_series_fill(df, other, level=None, fill_value=None, axis=0):
            return func(df, other, axis=axis, level=level, fill_value=fill_value)

        def call_series_no_fill(df, other, level=None, axis=0):
            return func(df, other, axis=axis, level=level)

        if issubclass(cls, DATAFRAME_TYPE):
            call = call_df_fill if 'fill_value' in func.__code__.co_varnames else call_df_no_fill
        elif issubclass(cls, SERIES_TYPE):
            call = call_series_fill if 'fill_value' in func.__code__.co_varnames else call_series_no_fill
        else:
            call = None
        return _register_method(cls, name, func, wrapper=call)

    # register mars unary ufuncs
    unary_ops = [
        DataFrameAbs, DataFrameLog, DataFrameLog2, DataFrameLog10,
        DataFrameSin, DataFrameCos, DataFrameTan,
        DataFrameSinh, DataFrameCosh, DataFrameTanh,
        DataFrameArcsin, DataFrameArccos, DataFrameArctan,
        DataFrameArcsinh, DataFrameArccosh, DataFrameArctanh,
        DataFrameRadians, DataFrameDegrees,
        DataFrameCeil, DataFrameFloor, DataFrameAround,
        DataFrameExp, DataFrameExp2, DataFrameExpm1,
        DataFrameSqrt, DataFrameNot, DataFrameIsNan,
        DataFrameIsInf, DataFrameIsFinite, DataFrameNegative
    ]
    for unary_op in unary_ops:
        register_tensor_unary_ufunc(unary_op)

    for entity in DATAFRAME_TYPE + SERIES_TYPE:
        setattr(entity, '__abs__', abs_)
        setattr(entity, 'abs', abs_)
        _register_method(entity, 'round', around)
        setattr(entity, '__invert__', logical_not)

        setattr(entity, '__add__', wrap_notimplemented_exception(add))
        setattr(entity, '__radd__', wrap_notimplemented_exception(radd))
        _register_bin_method(entity, 'add', add)
        _register_bin_method(entity, 'radd', radd)

        setattr(entity, '__sub__', wrap_notimplemented_exception(subtract))
        setattr(entity, '__rsub__', wrap_notimplemented_exception(rsubtract))
        _register_bin_method(entity, 'sub', subtract)
        _register_bin_method(entity, 'rsub', rsubtract)

        setattr(entity, '__mul__', wrap_notimplemented_exception(mul))
        setattr(entity, '__rmul__', wrap_notimplemented_exception(rmul))
        _register_bin_method(entity, 'mul', mul)
        _register_bin_method(entity, 'multiply', mul)
        _register_bin_method(entity, 'rmul', rmul)

        setattr(entity, '__floordiv__', wrap_notimplemented_exception(floordiv))
        setattr(entity, '__rfloordiv__', wrap_notimplemented_exception(rfloordiv))
        setattr(entity, '__truediv__', wrap_notimplemented_exception(truediv))
        setattr(entity, '__rtruediv__', wrap_notimplemented_exception(rtruediv))
        setattr(entity, '__div__', wrap_notimplemented_exception(truediv))
        setattr(entity, '__rdiv__', wrap_notimplemented_exception(rtruediv))
        _register_bin_method(entity, 'floordiv', floordiv)
        _register_bin_method(entity, 'rfloordiv', rfloordiv)
        _register_bin_method(entity, 'truediv', truediv)
        _register_bin_method(entity, 'rtruediv', rtruediv)
        _register_bin_method(entity, 'div', truediv)
        _register_bin_method(entity, 'rdiv', rtruediv)

        setattr(entity, '__mod__', wrap_notimplemented_exception(mod))
        setattr(entity, '__rmod__', wrap_notimplemented_exception(rmod))
        _register_bin_method(entity, 'mod', mod)
        _register_bin_method(entity, 'rmod', rmod)

        setattr(entity, '__pow__', wrap_notimplemented_exception(power))
        setattr(entity, '__rpow__', wrap_notimplemented_exception(rpower))
        _register_bin_method(entity, 'pow', power)
        _register_bin_method(entity, 'rpow', rpower)

        setattr(entity, '__eq__', _wrap_eq())
        setattr(entity, '__ne__', _wrap_comparison(ne))
        setattr(entity, '__lt__', _wrap_comparison(lt))
        setattr(entity, '__gt__', _wrap_comparison(gt))
        setattr(entity, '__ge__', _wrap_comparison(ge))
        setattr(entity, '__le__', _wrap_comparison(le))
        _register_bin_method(entity, 'eq', eq)
        _register_bin_method(entity, 'ne', ne)
        _register_bin_method(entity, 'lt', lt)
        _register_bin_method(entity, 'gt', gt)
        _register_bin_method(entity, 'ge', ge)
        _register_bin_method(entity, 'le', le)

        setattr(entity, '__matmul__', dot)
        _register_method(entity, 'dot', dot)

        setattr(entity, '__and__', wrap_notimplemented_exception(logical_and))
        setattr(entity, '__rand__', wrap_notimplemented_exception(logical_rand))

        setattr(entity, '__or__', wrap_notimplemented_exception(logical_or))
        setattr(entity, '__ror__', wrap_notimplemented_exception(logical_ror))

        setattr(entity, '__xor__', wrap_notimplemented_exception(logical_xor))
        setattr(entity, '__rxor__', wrap_notimplemented_exception(logical_rxor))

        setattr(entity, '__neg__', wrap_notimplemented_exception(negative))

    for entity in INDEX_TYPE:
        setattr(entity, '__eq__', _wrap_eq())