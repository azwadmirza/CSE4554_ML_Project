def parse_routine(name, args, types):
    """
    Generate thunk and method code for a given routine.

    Parameters
    ----------
    name : str
        Name of the C++ routine
    args : str
        Argument list specification (in format explained above)
    types : list
        List of types to instantiate, as returned `get_thunk_type_set`

    """

    ret_spec = args[0]
    arg_spec = args[1:]

    def get_arglist(I_type, T_type):
        """
        Generate argument list for calling the C++ function
        """
        args = []
        next_is_writeable = False
        j = 0
        for t in arg_spec:
            const = '' if next_is_writeable else 'const '
            next_is_writeable = False
            if t == '*':
                next_is_writeable = True
                continue
            elif t == 'i':
                args.append("*(%s*)a[%d]" % (const + I_type, j))
            elif t == 'I':
                args.append("(%s*)a[%d]" % (const + I_type, j))
            elif t == 'T':
                args.append("(%s*)a[%d]" % (const + T_type, j))
            elif t == 'B':
                args.append("(npy_bool_wrapper*)a[%d]" % (j,))
            elif t == 'V':
                if const:
                    raise ValueError("'V' argument must be an output arg")
                args.append("(std::vector<%s>*)a[%d]" % (I_type, j,))
            elif t == 'W':
                if const:
                    raise ValueError("'W' argument must be an output arg")
                args.append("(std::vector<%s>*)a[%d]" % (T_type, j,))
            elif t == 'l':
                args.append("*(%snpy_int64*)a[%d]" % (const, j))
            else:
                raise ValueError("Invalid spec character %r" % (t,))
            j += 1
        return ", ".join(args)

    # Generate thunk code: a giant switch statement with different
    # type combinations inside.
    thunk_content = """int j = get_thunk_case(I_typenum, T_typenum);
    switch (j) {"""
    for j, I_typenum, T_typenum, I_type, T_type in types:
        arglist = get_arglist(I_type, T_type)
        if T_type is None:
            dispatch = "%s" % (I_type,)
        else:
            dispatch = "%s,%s" % (I_type, T_type)
        if 'B' in arg_spec:
            dispatch += ",npy_bool_wrapper"

        piece = """
        case %(j)s:"""
        if ret_spec == 'v':
            piece += """
            (void)%(name)s<%(dispatch)s>(%(arglist)s);
            return 0;"""
        else:
            piece += """
            return %(name)s<%(dispatch)s>(%(arglist)s);"""
        thunk_content += piece % dict(j=j, I_type=I_type, T_type=T_type,
                                      I_typenum=I_typenum, T_typenum=T_typenum,
                                      arglist=arglist, name=name,
                                      dispatch=dispatch)

    thunk_content += """
    default:
        throw std::runtime_error("internal error: invalid argument typenums");
    }"""

    thunk_code = THUNK_TEMPLATE % dict(name=name,
                                       thunk_content=thunk_content)

    # Generate method code
    method_code = METHOD_TEMPLATE % dict(name=name,
                                         ret_spec=ret_spec,
                                         arg_spec=arg_spec)

    return thunk_code, method_code