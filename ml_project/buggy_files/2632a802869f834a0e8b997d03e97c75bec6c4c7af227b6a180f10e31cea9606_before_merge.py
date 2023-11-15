    def accept_loop(self, body: Union[IfStmt, Block], else_body: Block = None) -> Type:
        """Repeatedly type check a loop body until the frame doesn't change.

        Then check the else_body.
        """
        # The outer frame accumulates the results of all iterations
        with self.binder.frame_context(1) as outer_frame:
            self.binder.push_loop_frame()
            while True:
                with self.binder.frame_context(1):
                    # We may skip each iteration
                    self.binder.options_on_return[-1].append(outer_frame)
                    self.accept(body)
                if not self.binder.last_pop_changed:
                    break
            self.binder.pop_loop_frame()
            if else_body:
                self.accept(else_body)