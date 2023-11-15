    def visit_continue_stmt(self, s: ContinueStmt) -> Type:
        self.binder.breaking_out = True
        self.binder.allow_jump(self.binder.loop_frames[-1])
        return None