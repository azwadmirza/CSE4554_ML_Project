    def is_defined_type_var(self, tvar: str, context: Context) -> bool:
        return (self.tvar_scope is not None and
                self.tvar_scope.get_binding(self.lookup(tvar, context)) is not None)