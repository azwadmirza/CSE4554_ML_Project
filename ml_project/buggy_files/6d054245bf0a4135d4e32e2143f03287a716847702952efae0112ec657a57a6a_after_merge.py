    def _check_fors(self, node: ast.comprehension) -> None:
        parent = getattr(node, 'wps_parent', node)
        self._fors[parent] = len(parent.generators)