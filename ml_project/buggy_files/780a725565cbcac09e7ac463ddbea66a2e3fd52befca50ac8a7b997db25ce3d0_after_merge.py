    def visit_try_stmt(self, s: TryStmt) -> Type:
        """Type check a try statement."""
        # Our enclosing frame will get the result if the try/except falls through.
        # This one gets all possible states after the try block exited abnormally
        # (by exception, return, break, etc.)
        with self.binder.frame_context(can_skip=False, fall_through=0):
            # Not only might the body of the try statement exit
            # abnormally, but so might an exception handler or else
            # clause. The finally clause runs in *all* cases, so we
            # need an outer try frame to catch all intermediate states
            # in case an exception is raised during an except or else
            # clause. As an optimization, only create the outer try
            # frame when there actually is a finally clause.
            self.visit_try_without_finally(s, try_frame=bool(s.finally_body))
            if s.finally_body:
                # First we check finally_body is type safe on all abnormal exit paths
                self.accept(s.finally_body)

        if s.finally_body:
            # Then we try again for the more restricted set of options
            # that can fall through. (Why do we need to check the
            # finally clause twice? Depending on whether the finally
            # clause was reached by the try clause falling off the end
            # or exiting abnormally, after completing the finally clause
            # either flow will continue to after the entire try statement
            # or the exception/return/etc. will be processed and control
            # flow will escape. We need to check that the finally clause
            # type checks in both contexts, but only the resulting types
            # from the latter context affect the type state in the code
            # that follows the try statement.)
            self.accept(s.finally_body)

        return None