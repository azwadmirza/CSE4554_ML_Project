def _get_callee_args(call_expr, callee, loc, func_ir):
    """Get arguments for calling 'callee', including the default arguments.
    keyword arguments are currently only handled when 'callee' is a function.
    """
    if call_expr.op == 'call':
        args = list(call_expr.args)
    elif call_expr.op == 'getattr':
        args = [call_expr.value]
    else:
        raise TypeError("Unsupported ir.Expr.{}".format(call_expr.op))

    debug_print = _make_debug_print("inline_closure_call default handling")

    # handle defaults and kw arguments using pysignature if callee is function
    if isinstance(callee, pytypes.FunctionType):
        pysig = numba.utils.pysignature(callee)
        normal_handler = lambda index, param, default: default
        default_handler = lambda index, param, default: ir.Const(default, loc)
        # Throw error for stararg
        # TODO: handle stararg
        def stararg_handler(index, param, default):
            raise NotImplementedError(
                "Stararg not supported in inliner for arg {} {}".format(
                    index, param))
        if call_expr.op == 'call':
            kws = dict(call_expr.kws)
        else:
            kws = {}
        return numba.typing.fold_arguments(
            pysig, args, kws, normal_handler, default_handler,
            stararg_handler)
    else:
        # TODO: handle arguments for make_function case similar to function
        # case above
        callee_defaults = (callee.defaults if hasattr(callee, 'defaults')
                           else callee.__defaults__)
        if callee_defaults:
            debug_print("defaults = ", callee_defaults)
            if isinstance(callee_defaults, tuple):  # Python 3.5
                defaults_list = []
                for x in callee_defaults:
                    if isinstance(x, ir.Var):
                        defaults_list.append(x)
                    else:
                        # this branch is predominantly for kwargs from
                        # inlinable functions
                        defaults_list.append(ir.Const(value=x, loc=loc))
                args = args + defaults_list
            elif (isinstance(callee_defaults, ir.Var)
                    or isinstance(callee_defaults, str)):
                default_tuple = func_ir.get_definition(callee_defaults)
                assert(isinstance(default_tuple, ir.Expr))
                assert(default_tuple.op == "build_tuple")
                const_vals = [func_ir.get_definition(x) for
                              x in default_tuple.items]
                args = args + const_vals
            else:
                raise NotImplementedError(
                    "Unsupported defaults to make_function: {}".format(
                        defaults))
        return args