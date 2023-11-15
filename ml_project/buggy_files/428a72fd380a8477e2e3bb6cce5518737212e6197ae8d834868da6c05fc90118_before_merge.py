    def visit_raise_stmt(self, s: RaiseStmt) -> Type:
        """Type check a raise statement."""
        self.binder.breaking_out = True
        if s.expr:
            self.type_check_raise(s.expr, s)
        if s.from_expr:
            self.type_check_raise(s.from_expr, s)