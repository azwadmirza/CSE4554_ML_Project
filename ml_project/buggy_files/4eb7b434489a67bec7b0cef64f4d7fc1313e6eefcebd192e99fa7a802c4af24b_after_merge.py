    def visit_return_stmt(self, s: ReturnStmt) -> Type:
        """Type check a return statement."""
        self.check_return_stmt(s)
        self.binder.unreachable()