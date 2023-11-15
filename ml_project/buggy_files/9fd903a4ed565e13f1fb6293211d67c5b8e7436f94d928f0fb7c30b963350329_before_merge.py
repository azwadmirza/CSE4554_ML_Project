    def visit_for_stmt(self, s: ForStmt) -> None:
        self.analyze_lvalue(s.index)
        s.body.accept(self)