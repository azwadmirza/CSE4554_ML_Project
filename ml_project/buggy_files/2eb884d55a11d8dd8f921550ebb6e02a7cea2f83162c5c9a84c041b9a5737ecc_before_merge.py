    def visit_assignment_stmt(self, s: AssignmentStmt) -> None:
        self.analyze(s.type)
        if isinstance(s.rvalue, IndexExpr) and isinstance(s.rvalue.analyzed, TypeAliasExpr):
            self.analyze(s.rvalue.analyzed.type)
        if isinstance(s.rvalue, CallExpr):
            if isinstance(s.rvalue.analyzed, NewTypeExpr):
                self.analyze(s.rvalue.analyzed.old_type)
            if isinstance(s.rvalue.analyzed, TypedDictExpr):
                self.analyze(s.rvalue.analyzed.info.typeddict_type)
            if isinstance(s.rvalue.analyzed, NamedTupleExpr):
                self.analyze(s.rvalue.analyzed.info.tuple_type)
        super().visit_assignment_stmt(s)