    def visit_break_stmt(self, s: BreakStmt) -> Type:
        self.binder.breaking_out = True
        self.binder.allow_jump(self.binder.loop_frames[-1] - 1)
        return None