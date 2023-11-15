    def accept_loop(self, body: Statement, else_body: Statement = None, *,
                    exit_condition: Expression = None) -> Type:
        """Repeatedly type check a loop body until the frame doesn't change.
        If exit_condition is set, assume it must be False on exit from the loop.

        Then check the else_body.
        """
        # The outer frame accumulates the results of all iterations
        with self.binder.frame_context(can_skip=False):
            while True:
                with self.binder.frame_context(can_skip=True,
                                               break_frame=2, continue_frame=1):
                    self.accept(body)
                if not self.binder.last_pop_changed:
                    break
            if exit_condition:
                _, else_map = self.find_isinstance_check(exit_condition)
                self.push_type_map(else_map)
            if else_body:
                self.accept(else_body)