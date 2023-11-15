    def visit_Name(self, node: ast.Name) -> None:
        if self._is_six(node, SIX_SIMPLE_ATTRS):
            self.six_simple[_ast_to_offset(node)] = node

        if self._scope_stack:
            if isinstance(node.ctx, ast.Load):
                self._scope_stack[-1].reads.add(node.id)
            elif isinstance(node.ctx, (ast.Store, ast.Del)):
                self._scope_stack[-1].writes.add(node.id)
            else:
                raise AssertionError(node)

        self.generic_visit(node)