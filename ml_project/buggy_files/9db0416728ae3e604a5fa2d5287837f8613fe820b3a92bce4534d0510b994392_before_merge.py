def inject_binary_ops(cls, inplace=False):
    for name in CMP_BINARY_OPS + NUM_BINARY_OPS:
        setattr(cls, op_str(name), cls._binary_op(get_op(name)))

    for name, f in [('eq', array_eq), ('ne', array_ne)]:
        setattr(cls, op_str(name), cls._binary_op(f))

    # patch in fillna
    f = _func_slash_method_wrapper(fillna)
    method = cls._binary_op(f, join='left', drop_missing_vars=False)
    setattr(cls, '_fillna', method)

    for name in NUM_BINARY_OPS:
        # only numeric operations have in-place and reflexive variants
        setattr(cls, op_str('r' + name),
                cls._binary_op(get_op(name), reflexive=True))
        if inplace:
            setattr(cls, op_str('i' + name),
                    cls._inplace_binary_op(get_op('i' + name)))