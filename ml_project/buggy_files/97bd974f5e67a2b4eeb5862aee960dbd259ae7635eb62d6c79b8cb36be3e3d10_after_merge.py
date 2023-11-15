    def visit_continue_stmt(self, s: ContinueStmt) -> Type:
        self.binder.handle_continue()
        return None