    def visit_continue_stmt(self, s: ContinueStmt) -> None:
        if self.loop_depth == 0:
            self.fail("'continue' outside loop", s, True)