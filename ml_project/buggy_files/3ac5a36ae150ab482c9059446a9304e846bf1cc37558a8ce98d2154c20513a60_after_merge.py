    def type_analyzer(self, *,
                      tvar_scope: Optional[TypeVarScope] = None,
                      allow_tuple_literal: bool = False,
                      aliasing: bool = False,
                      third_pass: bool = False) -> TypeAnalyser:
        if tvar_scope is None:
            tvar_scope = self.tvar_scope
        tpan = TypeAnalyser(self.lookup_qualified,
                            self.lookup_fully_qualified,
                            tvar_scope,
                            self.fail,
                            self.note,
                            self.plugin,
                            self.options,
                            self.is_typeshed_stub_file,
                            aliasing=aliasing,
                            allow_tuple_literal=allow_tuple_literal,
                            allow_unnormalized=self.is_stub_file,
                            third_pass=third_pass)
        tpan.in_dynamic_func = bool(self.function_stack and self.function_stack[-1].is_dynamic())
        tpan.global_scope = not self.type and not self.function_stack
        return tpan