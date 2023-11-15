    def get_generator_type(self, typdict, retty):
        gi = self.generator_info
        arg_types = [None] * len(self.arg_names)
        for index, name in self.arg_names.items():
            arg_types[index] = typdict[name]
        state_types = [typdict[var_name] for var_name in gi.state_vars]
        yield_types = [typdict[y.inst.value.name]
                       for y in gi.get_yield_points()]
        if not yield_types:
            msg = "Cannot type generator: it does not yield any value"
            raise TypingError(msg)
        yield_type = self.context.unify_types(*yield_types)
        if yield_type is None:
            msg = "Cannot type generator: cannot unify yielded types %s"
            raise TypingError(msg % (yield_types,))
        return types.Generator(self.func_id.func, yield_type, arg_types,
                               state_types, has_finalizer=True)