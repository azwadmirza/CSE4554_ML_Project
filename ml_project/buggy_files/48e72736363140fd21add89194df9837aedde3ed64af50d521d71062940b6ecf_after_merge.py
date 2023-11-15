    def anal_type(self, t: Type, *,
                  tvar_scope: Optional[TypeVarScope] = None,
                  allow_tuple_literal: bool = False,
                  aliasing: bool = False,
                  third_pass: bool = False) -> Type:
        if t:
            a = self.type_analyzer(
                tvar_scope=tvar_scope,
                aliasing=aliasing,
                allow_tuple_literal=allow_tuple_literal,
                third_pass=third_pass)
            return t.accept(a)

        else:
            return None