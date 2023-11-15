    def visit_for_stmt(self, s: ForStmt) -> None:
        self.analyze(s.index_type, s)
        super().visit_for_stmt(s)