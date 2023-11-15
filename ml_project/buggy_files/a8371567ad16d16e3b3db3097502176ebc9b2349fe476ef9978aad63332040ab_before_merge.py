    def _check_len_call(self, node: ast.Subscript) -> None:
        is_len_call = (
            isinstance(node.slice, ast.Index) and
            isinstance(node.slice.value, ast.BinOp) and
            isinstance(node.slice.value.op, ast.Sub) and
            self._is_wrong_len(
                node.slice.value,
                source.node_to_string(node.value),
            )
        )

        if is_len_call:
            self.add_violation(
                refactoring.ImplicitNegativeIndexViolation(node),
            )