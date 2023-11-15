    def _is_float_key(self, node: ast.Index) -> bool:
        real_node = operators.unwrap_unary_node(node.value)
        return (
            isinstance(real_node, ast.Num) and
            isinstance(real_node.n, float)
        )