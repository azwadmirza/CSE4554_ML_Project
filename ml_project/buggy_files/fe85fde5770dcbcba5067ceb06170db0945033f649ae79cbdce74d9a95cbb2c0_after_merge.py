    def visit_break_stmt(self, s: BreakStmt) -> Type:
        self.binder.handle_break()
        return None