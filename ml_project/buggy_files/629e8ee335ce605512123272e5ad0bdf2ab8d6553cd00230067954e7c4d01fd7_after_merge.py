    def visit_type_var(self, t: TypeVarType) -> None:
        if t.upper_bound:
            t.upper_bound.accept(self)
        if t.values:
            for v in t.values:
                v.accept(self)