    def tvar_scope_frame(self) -> Iterator[None]:
        old_scope = self.tvar_scope
        if self.tvar_scope:
            self.tvar_scope = self.tvar_scope.method_frame()
        else:
            assert self.third_pass, "Internal error: type variable scope not given"
        yield
        self.tvar_scope = old_scope