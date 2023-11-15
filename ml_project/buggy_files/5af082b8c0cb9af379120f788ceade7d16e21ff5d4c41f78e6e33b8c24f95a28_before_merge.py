def print_item_impl(context, builder, sig, args):
    """
    Print a single native value by boxing it in a Python object and
    invoking the Python interpreter's print routine.
    """
    ty, = sig.args
    val, = args

    pyapi = context.get_python_api(builder)

    if context.enable_nrt:
        context.nrt.incref(builder, ty, val)
    # XXX unfortunately, we don't have access to the env manager from here
    obj = pyapi.from_native_value(ty, val)
    with builder.if_else(cgutils.is_not_null(builder, obj), likely=True) as (if_ok, if_error):
        with if_ok:
            pyapi.print_object(obj)
            pyapi.decref(obj)
        with if_error:
            cstr = context.insert_const_string(builder.module,
                                               "the print() function")
            strobj = pyapi.string_from_string(cstr)
            pyapi.err_write_unraisable(strobj)
            pyapi.decref(strobj)

    res = context.get_dummy_value()
    return impl_ret_untracked(context, builder, sig.return_type, res)