def _create_shape_signature(
        get_shape_classes,
        num_inputs,
        num_reductions,
        args,
        func_sig,
        races):
    '''Create shape signature for GUFunc
    '''
    if config.DEBUG_ARRAY_OPT:
        print("_create_shape_signature", num_inputs, num_reductions, args, func_sig)
        for i in args[1:]:
            print("argument", i, type(i), get_shape_classes(i))

    num_inouts = len(args) - num_reductions
    # maximum class number for array shapes
    classes = [get_shape_classes(var) if var not in races else (-1,) for var in args[1:]]
    class_set = set()
    for _class in classes:
        if _class:
            for i in _class:
                class_set.add(i)
    max_class = max(class_set) + 1 if class_set else 0
    classes.insert(0, (max_class,)) # force set the class of 'sched' argument
    class_set.add(max_class)
    class_map = {}
    # TODO: use prefix + class number instead of single char
    alphabet = ord('a')
    for n in class_set:
       if n >= 0:
           class_map[n] = chr(alphabet)
           alphabet += 1

    alpha_dict = {'latest_alpha' : alphabet}

    def bump_alpha(c, class_map):
        if c >= 0:
            return class_map[c]
        else:
            alpha_dict['latest_alpha'] += 1
            return chr(alpha_dict['latest_alpha'])

    gu_sin = []
    gu_sout = []
    count = 0
    syms_sin = ()
    for cls in classes:
        # print("create_shape_signature: var = ", var, " typ = ", typ)
        count = count + 1
        if cls:
            dim_syms = tuple(bump_alpha(c, class_map) for c in cls)
        else:
            dim_syms = ()
        if (count > num_inouts):
            # assume all reduction vars are scalar
            gu_sout.append(())
        elif count > num_inputs and all([s in syms_sin for s in dim_syms]):
            # only when dim_syms are found in gu_sin, we consider this as
            # output
            gu_sout.append(dim_syms)
        else:
            gu_sin.append(dim_syms)
            syms_sin += dim_syms
    return (gu_sin, gu_sout)