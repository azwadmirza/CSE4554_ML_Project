    def visit_instance(self, t: Instance) -> Type:
        info = t.type
        for (i, arg), tvar in zip(enumerate(t.args), info.defn.type_vars):
            if tvar.values:
                if isinstance(arg, TypeVarType):
                    arg_values = arg.values
                    if not arg_values:
                        self.fail('Type variable "{}" not valid as type '
                                  'argument value for "{}"'.format(
                                      arg.name, info.name()), t)
                        continue
                else:
                    arg_values = [arg]
                self.check_type_var_values(info, arg_values, tvar.name, tvar.values, i + 1, t)
            if not is_subtype(arg, tvar.upper_bound):
                self.fail('Type argument "{}" of "{}" must be '
                          'a subtype of "{}"'.format(
                              arg, info.name(), tvar.upper_bound), t)
        return super().visit_instance(t)