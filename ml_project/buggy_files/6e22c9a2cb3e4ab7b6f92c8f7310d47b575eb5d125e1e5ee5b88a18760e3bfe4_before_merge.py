    def visit_assert_stmt(self, s: AssertStmt) -> Type:
        self.accept(s.expr)

        # If this is asserting some isinstance check, bind that type in the following code
        true_map, _ = find_isinstance_check(s.expr, self.type_map)

        if true_map:
            for var, type in true_map.items():
                self.binder.push(var, type)