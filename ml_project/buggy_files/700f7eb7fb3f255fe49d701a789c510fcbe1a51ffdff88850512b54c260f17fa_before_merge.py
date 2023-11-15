    def visit_call_expr(self, expr: CallExpr) -> None:
        """Analyze a call expression.

        Some call expressions are recognized as special forms, including
        cast(...).
        """
        if expr.analyzed:
            return
        expr.callee.accept(self)
        if refers_to_fullname(expr.callee, 'typing.cast'):
            # Special form cast(...).
            if not self.check_fixed_args(expr, 2, 'cast'):
                return
            # Translate first argument to an unanalyzed type.
            try:
                target = expr_to_unanalyzed_type(expr.args[0])
            except TypeTranslationError:
                self.fail('Cast target is not a type', expr)
                return
            # Piggyback CastExpr object to the CallExpr object; it takes
            # precedence over the CallExpr semantics.
            expr.analyzed = CastExpr(expr.args[1], target)
            expr.analyzed.line = expr.line
            expr.analyzed.accept(self)
        elif refers_to_fullname(expr.callee, 'builtins.reveal_type'):
            if not self.check_fixed_args(expr, 1, 'reveal_type'):
                return
            expr.analyzed = RevealExpr(kind=REVEAL_TYPE, expr=expr.args[0])
            expr.analyzed.line = expr.line
            expr.analyzed.column = expr.column
            expr.analyzed.accept(self)
        elif refers_to_fullname(expr.callee, 'builtins.reveal_locals'):
            # Store the local variable names into the RevealExpr for use in the
            # type checking pass
            local_nodes = []  # type: List[Var]
            if self.is_module_scope():
                # try to determine just the variable declarations in module scope
                # self.globals.values() contains SymbolTableNode's
                # Each SymbolTableNode has an attribute node that is nodes.Var
                # look for variable nodes that marked as is_inferred
                # Each symboltable node has a Var node as .node
                local_nodes = cast(
                    List[Var],
                    [
                        n.node for name, n in self.globals.items()
                        if getattr(n.node, 'is_inferred', False)
                    ]
                )
            elif self.is_class_scope():
                # type = None  # type: Optional[TypeInfo]
                if self.type is not None:
                    local_nodes = cast(List[Var], [st.node for st in self.type.names.values()])
            elif self.is_func_scope():
                # locals = None  # type: List[Optional[SymbolTable]]
                if self.locals is not None:
                    symbol_table = self.locals[-1]
                    if symbol_table is not None:
                        local_nodes = cast(List[Var], [st.node for st in symbol_table.values()])
            expr.analyzed = RevealExpr(kind=REVEAL_LOCALS, local_nodes=local_nodes)
            expr.analyzed.line = expr.line
            expr.analyzed.column = expr.column
            expr.analyzed.accept(self)
        elif refers_to_fullname(expr.callee, 'typing.Any'):
            # Special form Any(...) no longer supported.
            self.fail('Any(...) is no longer supported. Use cast(Any, ...) instead', expr)
        elif refers_to_fullname(expr.callee, 'typing._promote'):
            # Special form _promote(...).
            if not self.check_fixed_args(expr, 1, '_promote'):
                return
            # Translate first argument to an unanalyzed type.
            try:
                target = expr_to_unanalyzed_type(expr.args[0])
            except TypeTranslationError:
                self.fail('Argument 1 to _promote is not a type', expr)
                return
            expr.analyzed = PromoteExpr(target)
            expr.analyzed.line = expr.line
            expr.analyzed.accept(self)
        elif refers_to_fullname(expr.callee, 'builtins.dict'):
            expr.analyzed = self.translate_dict_call(expr)
        elif refers_to_fullname(expr.callee, 'builtins.divmod'):
            if not self.check_fixed_args(expr, 2, 'divmod'):
                return
            expr.analyzed = OpExpr('divmod', expr.args[0], expr.args[1])
            expr.analyzed.line = expr.line
            expr.analyzed.accept(self)
        else:
            # Normal call expression.
            for a in expr.args:
                a.accept(self)

            if (isinstance(expr.callee, MemberExpr) and
                    isinstance(expr.callee.expr, NameExpr) and
                    expr.callee.expr.name == '__all__' and
                    expr.callee.expr.kind == GDEF and
                    expr.callee.name in ('append', 'extend')):
                if expr.callee.name == 'append' and expr.args:
                    self.add_exports(expr.args[0])
                elif (expr.callee.name == 'extend' and expr.args and
                        isinstance(expr.args[0], (ListExpr, TupleExpr))):
                    self.add_exports(expr.args[0].items)