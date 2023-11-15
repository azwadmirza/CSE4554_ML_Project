    def is_true(self, builder, typ, val):
        """
        Return the truth value of a value of the given Numba type.
        """
        fnty = self.typing_context.resolve_value_type(bool)
        sig = fnty.get_call_type(self.typing_context, (typ,), {})
        impl = self.get_function(fnty, sig)
        return impl(builder, (val,))