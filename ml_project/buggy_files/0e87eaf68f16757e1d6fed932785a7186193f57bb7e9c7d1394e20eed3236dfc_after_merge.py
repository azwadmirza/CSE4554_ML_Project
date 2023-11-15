    def _check_method(self, node: AnyFunctionDef) -> None:
        parent = getattr(node, 'wps_parent', None)
        if isinstance(parent, ast.ClassDef):
            self._methods[parent] += 1