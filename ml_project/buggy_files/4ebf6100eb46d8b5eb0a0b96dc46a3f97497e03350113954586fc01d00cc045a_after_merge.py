    def visit_collection(self, node: AnyCollection) -> None:
        """Checks how collection items indentation."""
        if isinstance(node, ast.Dict):
            elements = normalize_dict_elements(node)
        else:
            elements = node.elts
        self._check_indentation(node, elements, extra_lines=1)
        self.generic_visit(node)