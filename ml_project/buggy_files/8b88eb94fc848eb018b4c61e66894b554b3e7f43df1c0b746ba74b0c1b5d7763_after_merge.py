def _prepare_argument(ctxt, bld, inp, tyinp, where='input operand'):
    """returns an instance of the appropriate Helper (either
    _ScalarHelper or _ArrayHelper) class to handle the argument.
    using the polymorphic interface of the Helper classes, scalar
    and array cases can be handled with the same code"""

    # first un-Optional Optionals
    if isinstance(tyinp, types.Optional):
        oty = tyinp
        tyinp = tyinp.type
        inp = ctxt.cast(bld, inp, oty, tyinp)

    # then prepare the arg for a concrete instance
    if isinstance(tyinp, types.ArrayCompatible):
        ary     = ctxt.make_array(tyinp)(ctxt, bld, inp)
        shape   = cgutils.unpack_tuple(bld, ary.shape, tyinp.ndim)
        strides = cgutils.unpack_tuple(bld, ary.strides, tyinp.ndim)
        return _ArrayHelper(ctxt, bld, shape, strides, ary.data,
                            tyinp.layout, tyinp.dtype, tyinp.ndim, inp)
    elif types.unliteral(tyinp) in types.number_domain | set([types.boolean]):
        return _ScalarHelper(ctxt, bld, inp, tyinp)
    else:
        raise NotImplementedError('unsupported type for {0}: {1}'.format(where, str(tyinp)))