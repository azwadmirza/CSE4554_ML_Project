    def generic_compare(self, builder, key, argtypes, args):
        """
        Compare the given LLVM values of the given Numba types using
        the comparison *key* (e.g. '==').  The values are first cast to
        a common safe conversion type.
        """
        at, bt = argtypes
        av, bv = args
        ty = self.typing_context.unify_types(at, bt)
        assert ty is not None
        cav = self.cast(builder, av, at, ty)
        cbv = self.cast(builder, bv, bt, ty)
        fnty = self.typing_context.resolve_value_type(key)
        cmpsig = fnty.get_call_type(self.typing_context, argtypes, {})
        cmpfunc = self.get_function(fnty, cmpsig)
        self.add_linking_libs(getattr(cmpfunc, 'libs', ()))
        return cmpfunc(builder, (cav, cbv))