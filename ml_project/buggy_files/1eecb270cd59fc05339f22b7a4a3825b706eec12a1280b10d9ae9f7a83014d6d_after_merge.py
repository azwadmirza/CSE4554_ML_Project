def convert_code_obj_to_function(code_obj, caller_ir):
    """
    Converts a code object from a `make_function.code` attr in the IR into a
    python function, caller_ir is the FunctionIR of the caller and is used for
    the resolution of freevars.
    """
    fcode = code_obj.code
    nfree = len(fcode.co_freevars)

    # try and resolve freevars if they are consts in the caller's IR
    # these can be baked into the new function
    freevars = []
    for x in fcode.co_freevars:
        # not using guard here to differentiate between multiple definition and
        # non-const variable
        try:
            freevar_def = caller_ir.get_definition(x)
        except KeyError:
            msg = ("Cannot capture a constant value for variable '%s' as there "
                   "are multiple definitions present." % x)
            raise TypingError(msg, loc=code_obj.loc)
        if isinstance(freevar_def, ir.Const):
            freevars.append(freevar_def.value)
        else:
            msg = ("Cannot capture the non-constant value associated with "
                   "variable '%s' in a function that will escape." % x)
            raise TypingError(msg, loc=code_obj.loc)

    func_env = "\n".join(["  c_%d = %s" % (i, x) for i, x in enumerate(freevars)])
    func_clo = ",".join(["c_%d" % i for i in range(nfree)])
    co_varnames = list(fcode.co_varnames)

    # This is horrible. The code object knows about the number of args present
    # it also knows the name of the args but these are bundled in with other
    # vars in `co_varnames`. The make_function IR node knows what the defaults
    # are, they are defined in the IR as consts. The following finds the total
    # number of args (args + kwargs with defaults), finds the default values
    # and infers the number of "kwargs with defaults" from this and then infers
    # the number of actual arguments from that.
    n_kwargs = 0
    n_allargs = fcode.co_argcount
    kwarg_defaults = caller_ir.get_definition(code_obj.defaults)
    if kwarg_defaults is not None:
        if isinstance(kwarg_defaults, tuple):
            d = [caller_ir.get_definition(x).value for x in kwarg_defaults]
            kwarg_defaults_tup = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value
                 for x in kwarg_defaults.items]
            kwarg_defaults_tup = tuple(d)
        n_kwargs = len(kwarg_defaults_tup)
    nargs = n_allargs - n_kwargs

    func_arg = ",".join(["%s" % (co_varnames[i]) for i in range(nargs)])
    if n_kwargs:
        kw_const = ["%s = %s" % (co_varnames[i + nargs], kwarg_defaults_tup[i])
                    for i in range(n_kwargs)]
        func_arg += ", "
        func_arg += ", ".join(kw_const)

    # globals are the same as those in the caller
    glbls = caller_ir.func_id.func.__globals__

    # create the function and return it
    return _create_function_from_code_obj(fcode, func_env, func_arg, func_clo,
                                          glbls)