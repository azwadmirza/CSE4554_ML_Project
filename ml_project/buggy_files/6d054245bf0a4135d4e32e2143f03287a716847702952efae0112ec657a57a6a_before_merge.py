    def _check_fors(self, node: ast.comprehension) -> None:
        parent = getattr(node, 'parent', node)
        self._fors[parent] = len(parent.generators)