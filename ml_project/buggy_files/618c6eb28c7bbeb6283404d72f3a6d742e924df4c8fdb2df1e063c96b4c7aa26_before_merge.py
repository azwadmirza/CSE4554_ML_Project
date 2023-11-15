    def lower_inplace_operator(context, builder, sig, args):
        # The visible signature is (A, B) -> A
        # The implementation's signature (with explicit output)
        # is (A, B, A) -> A
        args = args + (args[0],)
        sig = typing.signature(sig.return_type, *sig.args + (sig.args[0],))
        return numpy_ufunc_kernel(context, builder, sig, args, kernel,
                                  explicit_output=True)