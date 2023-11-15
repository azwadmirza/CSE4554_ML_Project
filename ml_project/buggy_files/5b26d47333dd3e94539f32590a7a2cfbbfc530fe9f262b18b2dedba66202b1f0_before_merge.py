    def analyze_alias(self, rvalue: Expression,
                      allow_unnormalized: bool) -> Tuple[Optional[Type], List[str]]:
        """Check if 'rvalue' represents a valid type allowed for aliasing
        (e.g. not a type variable). If yes, return the corresponding type and a list of
        qualified type variable names for generic aliases.
        If 'allow_unnormalized' is True, allow types like builtins.list[T].
        """
        res = analyze_type_alias(rvalue,
                                 self.lookup_qualified,
                                 self.lookup_fully_qualified,
                                 self.tvar_scope,
                                 self.fail,
                                 self.plugin,
                                 self.options,
                                 self.is_typeshed_stub_file,
                                 allow_unnormalized=True)
        if res:
            alias_tvars = [name for (name, _) in
                           res.accept(TypeVariableQuery(self.lookup_qualified, self.tvar_scope))]
        else:
            alias_tvars = []
        return res, alias_tvars