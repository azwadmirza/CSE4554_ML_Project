    def visit_break_stmt(self, s: BreakStmt) -> None:
        if self.loop_depth == 0:
            self.fail("'break' outside loop", s, True)