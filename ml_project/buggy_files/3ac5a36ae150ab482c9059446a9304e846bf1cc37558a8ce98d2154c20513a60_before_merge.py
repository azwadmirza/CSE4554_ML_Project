    def type_analyzer(self, *,
                      tvar_scope: Optional[TypeVarScope] = None,
                      allow_tuple_literal: bool = False,
                      aliasing: bool = False) -> TypeAnalyser:
        if tvar_scope is None:
            tvar_scope = self.tvar_scope
        return TypeAnalyser(self.lookup_qualified,
                            self.lookup_fully_qualified,
                            tvar_scope,
                            self.fail,
                            self.plugin,
                            self.options,
                            self.is_typeshed_stub_file,
                            aliasing=aliasing,
                            allow_tuple_literal=allow_tuple_literal,
                            allow_unnormalized=self.is_stub_file)