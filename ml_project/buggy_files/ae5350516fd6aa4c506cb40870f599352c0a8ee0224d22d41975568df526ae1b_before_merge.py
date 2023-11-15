    def _lower_call_normal(self, fnty, expr, signature):
        # Normal function resolution
        self.debug_print("# calling normal function: {0}".format(fnty))
        self.debug_print("# signature: {0}".format(signature))
        if (isinstance(expr.func, ir.Intrinsic) or
                isinstance(fnty, types.ObjModeDispatcher)):
            argvals = expr.func.args
        else:
            argvals = self.fold_call_args(
                fnty, signature, expr.args, expr.vararg, expr.kws,
            )
        impl = self.context.get_function(fnty, signature)
        if signature.recvr:
            # The "self" object is passed as the function object
            # for bounded function
            the_self = self.loadvar(expr.func.name)
            # Prepend the self reference
            argvals = [the_self] + list(argvals)

        res = impl(self.builder, argvals, self.loc)
        return res