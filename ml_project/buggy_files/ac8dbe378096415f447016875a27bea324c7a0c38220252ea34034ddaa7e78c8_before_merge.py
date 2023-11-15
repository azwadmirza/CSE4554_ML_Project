    def fold_argument_types(self, args, kws):
        """
        Given positional and named argument types, fold keyword arguments
        and resolve defaults by inserting types.Omitted() instances.

        A (pysig, argument types) tuple is returned.
        """
        def normal_handler(index, param, value):
            return value
        def default_handler(index, param, default):
            return types.Omitted(default)
        def stararg_handler(index, param, values):
            return types.Tuple(values)
        # For now, we take argument values from the @jit function, even
        # in the case of generated jit.
        args = fold_arguments(self.pysig, args, kws,
                              normal_handler,
                              default_handler,
                              stararg_handler)
        return self.pysig, args