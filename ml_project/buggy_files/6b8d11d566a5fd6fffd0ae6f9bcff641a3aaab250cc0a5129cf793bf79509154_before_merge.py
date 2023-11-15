    def visit_instance(self, t: Instance) -> None:
        info = t.type
        # Check type argument count.
        if len(t.args) != len(info.type_vars):
            if len(t.args) == 0:
                from_builtins = t.type.fullname() in nongen_builtins and not t.from_generic_builtin
                if ('generics' in self.options.disallow_any and
                        not self.is_typeshed_stub and
                        from_builtins):
                    alternative = nongen_builtins[t.type.fullname()]
                    self.fail(messages.IMPLICIT_GENERIC_ANY_BUILTIN.format(alternative), t)
                # Insert implicit 'Any' type arguments.
                if from_builtins:
                    # this 'Any' was already reported elsewhere
                    any_type = AnyType(TypeOfAny.special_form,
                                       line=t.line, column=t.column)
                else:
                    any_type = AnyType(TypeOfAny.from_omitted_generics,
                                       line=t.line, column=t.column)
                t.args = [any_type] * len(info.type_vars)
                return
            # Invalid number of type parameters.
            n = len(info.type_vars)
            s = '{} type arguments'.format(n)
            if n == 0:
                s = 'no type arguments'
            elif n == 1:
                s = '1 type argument'
            act = str(len(t.args))
            if act == '0':
                act = 'none'
            self.fail('"{}" expects {}, but {} given'.format(
                info.name(), s, act), t)
            # Construct the correct number of type arguments, as
            # otherwise the type checker may crash as it expects
            # things to be right.
            t.args = [AnyType(TypeOfAny.from_error) for _ in info.type_vars]
            t.invalid = True
        elif info.defn.type_vars:
            # Check type argument values.
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
        for arg in t.args:
            arg.accept(self)
        if info.is_newtype:
            for base in info.bases:
                base.accept(self)