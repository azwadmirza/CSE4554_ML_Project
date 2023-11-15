    def visit_with_stmt(self, s: WithStmt) -> None:
        self.analyze(s.target_type, s)
        super().visit_with_stmt(s)