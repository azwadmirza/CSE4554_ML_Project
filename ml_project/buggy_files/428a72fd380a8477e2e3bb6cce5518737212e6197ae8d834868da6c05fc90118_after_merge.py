    def visit_raise_stmt(self, s: RaiseStmt) -> Type:
        """Type check a raise statement."""
        if s.expr:
            self.type_check_raise(s.expr, s)
        if s.from_expr:
            self.type_check_raise(s.from_expr, s)
        self.binder.unreachable()