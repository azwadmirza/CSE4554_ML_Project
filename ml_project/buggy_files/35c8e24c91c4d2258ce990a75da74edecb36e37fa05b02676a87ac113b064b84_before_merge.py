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
        if yield_type is None or isinstance(yield_type, types.Optional):
            msg = "Cannot type generator: cannot unify yielded types %s"
            yp_highlights = []
            for y in gi.get_yield_points():
                msg = (_termcolor.errmsg("Yield of: IR '%s', type '%s', "
                                         "location: %s"))
                yp_highlights.append(msg % (str(y.inst),
                                            typdict[y.inst.value.name],
                                            y.inst.loc.strformat()))

            explain_ty = set()
            for ty in yield_types:
                if isinstance(ty, types.Optional):
                    explain_ty.add(ty.type)
                    explain_ty.add(types.NoneType('none'))
                else:
                    explain_ty.add(ty)
            raise TypingError("Can't unify yield type from the "
                              "following types: %s"
                              % ", ".join(sorted(map(str, explain_ty))) +
                              "\n\n" + "\n".join(yp_highlights))

        return types.Generator(self.func_id.func, yield_type, arg_types,
                               state_types, has_finalizer=True)