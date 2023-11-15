    def _check_nested_lambdas(self, node: ast.Lambda) -> None:
        parent = getattr(node, 'parent', None)
        if isinstance(parent, ast.Lambda):
            self.add_violation(NestedFunctionViolation(node))