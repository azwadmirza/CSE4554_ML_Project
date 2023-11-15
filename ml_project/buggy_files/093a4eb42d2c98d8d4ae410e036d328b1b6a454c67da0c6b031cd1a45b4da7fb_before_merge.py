    def _check_useless_math_operator(
        self,
        op: ast.operator,
        left: ast.AST,
        right: Optional[ast.AST] = None,
    ) -> None:
        if isinstance(left, ast.Num) and right:
            if left.n == 1:
                left = None
        non_negative_numbers = self._get_non_negative_nodes(left, right)

        for number in non_negative_numbers:
            forbidden = self._meaningless_operations.get(number.n, None)
            if forbidden and isinstance(op, forbidden):
                self.add_violation(
                    consistency.MeaninglessNumberOperationViolation(number),
                )