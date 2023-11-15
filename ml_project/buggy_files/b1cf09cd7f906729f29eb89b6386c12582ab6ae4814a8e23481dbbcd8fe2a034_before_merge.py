    def _check_float_key(self, node: ast.Subscript) -> None:
        is_float_key = (
            isinstance(node.slice, ast.Index) and
            self._is_float_key(node.slice)
        )

        if is_float_key:
            self.add_violation(best_practices.FloatKeyViolation(node))