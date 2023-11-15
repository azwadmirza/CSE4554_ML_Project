    def visit_instance(self, t: Instance) -> None:
        info = t.type
        if info.replaced or info.tuple_type:
            self.indicator['synthetic'] = True
        # Check type argument count.
        if len(t.args) != len(info.type_vars):
            if len(t.args) == 0:
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
            # Check type argument values. This is postponed to the end of semantic analysis
            # since we need full MROs and resolved forward references.
            for tvar in info.defn.type_vars:
                if (tvar.values
                        or not isinstance(tvar.upper_bound, Instance)
                        or tvar.upper_bound.type.fullname() != 'builtins.object'):
                    # Some restrictions on type variable. These can only be checked later
                    # after we have final MROs and forward references have been resolved.
                    self.indicator['typevar'] = True
        for arg in t.args:
            arg.accept(self)
        if info.is_newtype:
            for base in info.bases:
                base.accept(self)