    def visit_if_stmt(self, s: IfStmt) -> Type:
        """Type check an if statement."""
        breaking_out = True
        # This frame records the knowledge from previous if/elif clauses not being taken.
        with self.binder.frame_context():
            for e, b in zip(s.expr, s.body):
                t = self.accept(e)
                self.check_usable_type(t, e)
                if_map, else_map = find_isinstance_check(e, self.type_map)
                if if_map is None:
                    # The condition is always false
                    # XXX should issue a warning?
                    pass
                else:
                    # Only type check body if the if condition can be true.
                    with self.binder.frame_context(2):
                        if if_map:
                            for var, type in if_map.items():
                                self.binder.push(var, type)

                        self.accept(b)
                    breaking_out = breaking_out and self.binder.last_pop_breaking_out

                    if else_map:
                        for var, type in else_map.items():
                            self.binder.push(var, type)
                if else_map is None:
                    # The condition is always true => remaining elif/else blocks
                    # can never be reached.

                    # Might also want to issue a warning
                    # print("Warning: isinstance always true")
                    break
            else:  # Didn't break => can't prove one of the conditions is always true
                with self.binder.frame_context(2):
                    if s.else_body:
                        self.accept(s.else_body)
                breaking_out = breaking_out and self.binder.last_pop_breaking_out
        if breaking_out:
            self.binder.breaking_out = True
        return None