    def _check_expression(
        self,
        node: ast.Expr,
        is_first: bool = False,
    ) -> None:
        if isinstance(node.value, self._have_effect):
            return

        if is_first and is_doc_string(node):
            parent = getattr(node, 'parent', None)
            if isinstance(parent, self._have_doc_strings):
                return

        self.add_violation(StatementHasNoEffectViolation(node))