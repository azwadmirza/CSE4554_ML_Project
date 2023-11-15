def type_inference_stage(typingctx, interp, args, return_type, locals={},
                         raise_errors=True):
    if len(args) != interp.arg_count:
        raise TypeError("Mismatch number of argument types")

    warnings = errors.WarningsFixer(errors.NumbaWarning)
    infer = typeinfer.TypeInferer(typingctx, interp, warnings)
    with typingctx.callstack.register(infer, interp.func_id, args):
        # Seed argument types
        for index, (name, ty) in enumerate(zip(interp.arg_names, args)):
            infer.seed_argument(name, index, ty)

        # Seed return type
        if return_type is not None:
            infer.seed_return(return_type)

        # Seed local types
        for k, v in locals.items():
            infer.seed_type(k, v)

        infer.build_constraint()
        infer.propagate(raise_errors=raise_errors)
        typemap, restype, calltypes = infer.unify(raise_errors=raise_errors)

    # Output all Numba warnings
    warnings.flush()

    return typemap, restype, calltypes