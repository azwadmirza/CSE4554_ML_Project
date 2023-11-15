def register_binary_operator_kernel(op, kernel, inplace=False):
    def lower_binary_operator(context, builder, sig, args):
        return numpy_ufunc_kernel(context, builder, sig, args, kernel,
                                  explicit_output=False)

    def lower_inplace_operator(context, builder, sig, args):
        # The visible signature is (A, B) -> A
        # The implementation's signature (with explicit output)
        # is (A, B, A) -> A
        args = args + (args[0],)
        sig = typing.signature(sig.return_type, *sig.args + (sig.args[0],))
        return numpy_ufunc_kernel(context, builder, sig, args, kernel,
                                  explicit_output=True)

    _any = types.Any
    _arr_kind = types.Array
    formal_sigs = [(_arr_kind, _arr_kind), (_any, _arr_kind), (_arr_kind, _any)]
    for sig in formal_sigs:
        if not inplace:
            lower(op, *sig)(lower_binary_operator)
        else:
            lower(op, *sig)(lower_inplace_operator)