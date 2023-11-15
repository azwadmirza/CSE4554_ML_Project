    def _get_non_negative_nodes(
        self,
        left: Optional[ast.AST],
        right: Optional[ast.AST] = None,
    ):
        non_negative_numbers = []
        for node in filter(None, (left, right)):
            real_node = unwrap_unary_node(node)
            if not isinstance(real_node, ast.Num):
                continue

            if real_node.n not in self._meaningless_operations:
                continue

            if real_node.n == 1 and walk.is_contained(node, ast.USub):
                continue
            non_negative_numbers.append(real_node)
        return non_negative_numbers