    def visit_with_stmt(self, s: WithStmt) -> None:
        if self.sem.is_module_scope():
            for n in s.target:
                if n:
                    self.analyze_lvalue(n, explicit_type=s.target_type is not None)
            s.body.accept(self)