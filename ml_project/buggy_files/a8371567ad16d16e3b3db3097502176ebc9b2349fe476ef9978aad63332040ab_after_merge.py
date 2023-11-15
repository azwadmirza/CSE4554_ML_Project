    def _check_len_call(self, node: ast.Subscript) -> None:
        node_slice = get_slice_expr(node)
        is_len_call = (
            isinstance(node_slice, ast.BinOp) and
            isinstance(node_slice.op, ast.Sub) and
            self._is_wrong_len(
                node_slice,
                source.node_to_string(node.value),
            )
        )

        if is_len_call:
            self.add_violation(
                refactoring.ImplicitNegativeIndexViolation(node),
            )