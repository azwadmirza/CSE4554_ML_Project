    def visit_for_stmt(self, s: ForStmt) -> None:
        if self.sem.is_module_scope():
            self.analyze_lvalue(s.index, explicit_type=s.index_type is not None)
            s.body.accept(self)
            if s.else_body:
                s.else_body.accept(self)