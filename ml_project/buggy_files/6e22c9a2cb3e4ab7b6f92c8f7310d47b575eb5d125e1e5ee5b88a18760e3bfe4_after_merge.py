    def visit_assert_stmt(self, s: AssertStmt) -> Type:
        self.accept(s.expr)

        # If this is asserting some isinstance check, bind that type in the following code
        true_map, _ = self.find_isinstance_check(s.expr)

        self.push_type_map(true_map)