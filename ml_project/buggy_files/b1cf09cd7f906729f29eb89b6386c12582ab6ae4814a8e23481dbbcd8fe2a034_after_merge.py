    def _check_float_key(self, node: ast.Subscript) -> None:
        if self._is_float_key(get_slice_expr(node)):
            self.add_violation(best_practices.FloatKeyViolation(node))