    def visit_type_var(self, t: TypeVarType) -> Type:
        raise RuntimeError('TypeVarType is already analyzed')