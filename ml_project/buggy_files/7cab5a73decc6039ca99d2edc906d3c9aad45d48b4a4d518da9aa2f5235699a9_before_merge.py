    def is_true(self, builder, typ, val):
        """
        Return the truth value of a value of the given Numba type.
        """
        impl = self.get_function(bool, typing.signature(types.boolean, typ))
        return impl(builder, (val,))