    def visit_assignment_stmt(self, s: AssignmentStmt) -> None:
        """Traverse the assignment statement.

        This includes the actual assignment and synthetic types
        resulted from this assignment (if any). Currently this includes
        NewType, TypedDict, NamedTuple, and TypeVar.
        """
        self.analyze(s.type, s)
        if isinstance(s.rvalue, IndexExpr) and isinstance(s.rvalue.analyzed, TypeAliasExpr):
            self.analyze(s.rvalue.analyzed.type, s.rvalue.analyzed, warn=True)
        if isinstance(s.rvalue, CallExpr):
            analyzed = s.rvalue.analyzed
            if isinstance(analyzed, NewTypeExpr):
                self.analyze(analyzed.old_type, analyzed)
                if analyzed.info:
                    # Currently NewTypes only have __init__, but to be future proof,
                    # we analyze all symbols.
                    self.analyze_info(analyzed.info)
                if analyzed.info and analyzed.info.mro:
                    analyzed.info.mro = []  # Force recomputation
                    mypy.semanal.calculate_class_mro(analyzed.info.defn, self.fail_blocker)
            if isinstance(analyzed, TypeVarExpr):
                types = []
                if analyzed.upper_bound:
                    types.append(analyzed.upper_bound)
                if analyzed.values:
                    types.extend(analyzed.values)
                self.analyze_types(types, analyzed)
            if isinstance(analyzed, TypedDictExpr):
                self.analyze(analyzed.info.typeddict_type, analyzed, warn=True)
            if isinstance(analyzed, NamedTupleExpr):
                self.analyze(analyzed.info.tuple_type, analyzed, warn=True)
                self.analyze_info(analyzed.info)
        # We need to pay additional attention to assignments that define a type alias.
        # The resulting type is also stored in the 'type_override' attribute of
        # the corresponding SymbolTableNode.
        if isinstance(s.lvalues[0], RefExpr) and isinstance(s.lvalues[0].node, Var):
            self.analyze(s.lvalues[0].node.type, s.lvalues[0].node)
            if isinstance(s.lvalues[0], NameExpr):
                node = self.sem.lookup(s.lvalues[0].name, s, suppress_errors=True)
                if node:
                    self.analyze(node.type_override, node)
        super().visit_assignment_stmt(s)