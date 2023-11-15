    def _check_method(self, node: AnyFunctionDef) -> None:
        parent = getattr(node, 'parent', None)
        if isinstance(parent, ast.ClassDef):
            self._methods[parent] += 1