    def infer_partial_type(self, name: Var, lvalue: Lvalue, init_type: Type) -> bool:
        if isinstance(init_type, (NoneTyp, UninhabitedType)):
            partial_type = PartialType(None, name, [init_type])
        elif isinstance(init_type, Instance):
            fullname = init_type.type.fullname()
            if (isinstance(lvalue, NameExpr) and
                    (fullname == 'builtins.list' or
                     fullname == 'builtins.set' or
                     fullname == 'builtins.dict') and
                    all(isinstance(t, (NoneTyp, UninhabitedType)) for t in init_type.args)):
                partial_type = PartialType(init_type.type, name, init_type.args)
            else:
                return False
        else:
            return False
        self.set_inferred_type(name, lvalue, partial_type)
        self.partial_types[-1][name] = lvalue
        return True