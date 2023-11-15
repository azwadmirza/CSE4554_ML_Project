    def visit_while_stmt(self, s: WhileStmt) -> None:
        s.body.accept(self)
        if s.else_body:
            s.else_body.accept(self)