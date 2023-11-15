    def visit_instance(self, t: Instance) -> None:
        info = t.type
        if info.replaced or info.tuple_type:
            self.indicator['synthetic'] = True
        # Check type argument count.
        if len(t.args) != len(info.type_vars):
            fix_instance(t, self.fail)
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