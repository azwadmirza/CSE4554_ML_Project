    def visit_collection(self, node: AnyCollection) -> None:
        """Checks how collection items indentation."""
        elements = node.keys if isinstance(node, ast.Dict) else node.elts
        self._check_indentation(node, elements, extra_lines=1)
        self.generic_visit(node)