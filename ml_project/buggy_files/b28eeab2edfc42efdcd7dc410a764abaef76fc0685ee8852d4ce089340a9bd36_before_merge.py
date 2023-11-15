def _create_shape_signature(classes, num_inputs, num_reductions, args, func_sig):
    '''Create shape signature for GUFunc
    '''
    num_inouts = len(args) - num_reductions
    # maximum class number for array shapes
    max_shape_num = max(sum([list(x) for x in classes.values()], []))
    if config.DEBUG_ARRAY_OPT:
        print("create_shape_signature = ", max_shape_num)
    gu_sin = []
    gu_sout = []
    count = 0
    syms_sin = ()
    for var, typ in zip(args, func_sig.args):
        # print("create_shape_signature: var = ", var, " typ = ", typ)
        count = count + 1
        if isinstance(typ, types.Array):
            if var in classes:
                var_shape = classes[var]
                assert len(var_shape) == typ.ndim
            else:
                var_shape = []
                for i in range(typ.ndim):
                    max_shape_num = max_shape_num + 1
                    var_shape.append(max_shape_num)
            # TODO: use prefix + class number instead of single char
            dim_syms = tuple([ chr(97 + i) for i in var_shape ]) # chr(97) = 'a'
        else:
            dim_syms = ()
        if (count > num_inouts):
            # assume all reduction vars are scalar
            gu_sout.append(())
        elif count > num_inputs and all([s in syms_sin for s in dim_syms]):
            # only when dim_syms are found in gu_sin, we consider this as output
            gu_sout.append(dim_syms)
        else:
            gu_sin.append(dim_syms)
            syms_sin += dim_syms
    return (gu_sin, gu_sout)