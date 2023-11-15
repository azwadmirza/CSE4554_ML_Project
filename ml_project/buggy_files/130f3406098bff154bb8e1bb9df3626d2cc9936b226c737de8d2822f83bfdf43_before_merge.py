def raise_on_unsupported_feature(func_ir, typemap):
    """
    Helper function to walk IR and raise if it finds op codes
    that are unsupported. Could be extended to cover IR sequences
    as well as op codes. Intended use is to call it as a pipeline
    stage just prior to lowering to prevent LoweringErrors for known
    unsupported features.
    """
    gdb_calls = [] # accumulate calls to gdb/gdb_init
    
    # issue 2195: check for excessively large tuples
    for arg_name in func_ir.arg_names:
        if arg_name in typemap and \
           isinstance(typemap[arg_name], types.containers.UniTuple) and \
           typemap[arg_name].count > 1000:
            # Raise an exception when len(tuple) > 1000. The choice of this number (1000)
            # was entirely arbitrary
            msg = ("Tuple '{}' length must be smaller than 1000.\n"
                   "Large tuples lead to the generation of a prohibitively large "
                   "LLVM IR which causes excessive memory pressure "
                   "and large compile times.\n"
                   "As an alternative, the use of a 'list' is recommended in "
                   "place of a 'tuple' as lists do not suffer from this problem.".format(arg_name))
            raise UnsupportedError(msg, func_ir.loc)

    for blk in func_ir.blocks.values():
        for stmt in blk.find_insts(ir.Assign):
            # This raises on finding `make_function`
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value

                    # See if the construct name can be refined
                    code = getattr(val, 'code', None)
                    if code is not None:
                        # check if this is a closure, the co_name will
                        # be the captured function name which is not
                        # useful so be explicit
                        if getattr(val, 'closure', None) is not None:
                            use = '<creating a function from a closure>'
                            expr = ''
                        else:
                            use = code.co_name
                            expr = '(%s) ' % use
                    else:
                        use = '<could not ascertain use case>'
                        expr = ''

                    msg = ("Numba encountered the use of a language "
                            "feature it does not support in this context: "
                            "%s (op code: make_function not supported). If "
                            "the feature is explicitly supported it is "
                            "likely that the result of the expression %s"
                            "is being used in an unsupported manner.") % \
                            (use, expr)
                    raise UnsupportedError(msg, stmt.value.loc)

            # this checks for gdb initilization calls, only one is permitted
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue

                # check global function
                found = False
                if isinstance(val, pytypes.FunctionType):
                    found = val in {numba.gdb, numba.gdb_init}
                if not found: # freevar bind to intrinsic
                    found = getattr(val, '_name', "") == "gdb_internal"
                if found:
                    gdb_calls.append(stmt.loc) # report last seen location

            # this checks that np.<type> was called if view is called
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    df = func_ir.get_definition(var)
                    cn = guard(find_callname, func_ir, df)
                    if cn and cn[1] == 'numpy':
                        ty = getattr(numpy, cn[0])
                        if (numpy.issubdtype(ty, numpy.integer) or
                                numpy.issubdtype(ty, numpy.floating)):
                            continue

                    vardescr = '' if var.startswith('$') else "'{}' ".format(var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, "
                        "try wrapping the variable {}with 'np.<dtype>()'".
                        format(vardescr), loc=stmt.loc)

            # checks for globals that are also reflected
            if isinstance(stmt.value, ir.Global):
                ty = typemap[stmt.target.name]
                msg = ("Writing to a %s defined in globals is not "
                        "supported as globals are considered compile-time "
                        "constants.")
                if (getattr(ty, 'reflected', False) or
                    isinstance(ty, types.DictType)):
                    raise TypingError(msg % ty, loc=stmt.loc)

    # There is more than one call to function gdb/gdb_init
    if len(gdb_calls) > 1:
        msg = ("Calling either numba.gdb() or numba.gdb_init() more than once "
               "in a function is unsupported (strange things happen!), use "
               "numba.gdb_breakpoint() to create additional breakpoints "
               "instead.\n\nRelevant documentation is available here:\n"
               "http://numba.pydata.org/numba-doc/latest/user/troubleshoot.html"
               "/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-"
               "nopython-mode\n\nConflicting calls found at:\n %s")
        buf = '\n'.join([x.strformat() for x in gdb_calls])
        raise UnsupportedError(msg % buf)