    def visit_try_stmt(self, s: TryStmt) -> Type:
        """Type check a try statement."""
        # Our enclosing frame will get the result if the try/except falls through.
        # This one gets all possible intermediate states
        with self.binder.frame_context():
            if s.finally_body:
                self.binder.try_frames.add(len(self.binder.frames) - 1)
                breaking_out = self.visit_try_without_finally(s)
                self.binder.try_frames.remove(len(self.binder.frames) - 1)
                # First we check finally_body is type safe for all intermediate frames
                self.accept(s.finally_body)
                breaking_out = breaking_out or self.binder.breaking_out
            else:
                breaking_out = self.visit_try_without_finally(s)

        if not breaking_out and s.finally_body:
            # Then we try again for the more restricted set of options that can fall through
            self.accept(s.finally_body)
        self.binder.breaking_out = breaking_out
        return None