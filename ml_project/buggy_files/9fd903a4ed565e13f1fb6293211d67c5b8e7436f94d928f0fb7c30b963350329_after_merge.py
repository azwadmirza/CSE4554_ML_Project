    def visit_for_stmt(self, s: ForStmt) -> None:
        self.analyze_lvalue(s.index)
        s.body.accept(self)
        if s.else_body:
            s.else_body.accept(self)