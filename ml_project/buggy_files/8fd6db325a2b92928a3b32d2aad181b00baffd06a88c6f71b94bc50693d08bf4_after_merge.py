def _build_element_wise_ufunc_wrapper(cres, signature):
    '''Build a wrapper for the ufunc loop entry point given by the
    compilation result object, using the element-wise signature.
    '''
    ctx = cres.target_context
    library = cres.library
    fname = cres.fndesc.llvm_func_name

    env = cres.environment
    envptr = env.as_pointer(ctx)

    with compiler.lock_compiler:
        ptr = build_ufunc_wrapper(library, ctx, fname, signature,
                                cres.objectmode, envptr, env)

    # Get dtypes
    dtypenums = [as_dtype(a).num for a in signature.args]
    dtypenums.append(as_dtype(signature.return_type).num)
    return dtypenums, ptr, env