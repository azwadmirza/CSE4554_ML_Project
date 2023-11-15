    def visit_if_stmt(self, s: IfStmt) -> Type:
        """Type check an if statement."""
        # This frame records the knowledge from previous if/elif clauses not being taken.
        # Fall-through to the original frame is handled explicitly in each block.
        with self.binder.frame_context(can_skip=False, fall_through=0):
            for e, b in zip(s.expr, s.body):
                t = self.accept(e)
                self.check_usable_type(t, e)
                if_map, else_map = self.find_isinstance_check(e)

                # XXX Issue a warning if condition is always False?
                with self.binder.frame_context(can_skip=True, fall_through=2):
                    self.push_type_map(if_map)
                    self.accept(b)

                # XXX Issue a warning if condition is always True?
                self.push_type_map(else_map)

            with self.binder.frame_context(can_skip=False, fall_through=2):
                if s.else_body:
                    self.accept(s.else_body)
        return None