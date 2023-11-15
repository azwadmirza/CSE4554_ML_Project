    def visit_while_stmt(self, s: WhileStmt) -> Type:
        """Type check a while statement."""
        self.accept_loop(IfStmt([s.expr], [s.body], None), s.else_body,
                         exit_condition=s.expr)