    def closeness(expression):
        # type: (Tuple[List[Any], Any]) -> Tuple[int, int]
        # Prioritise expressions with a node closer to the statement executed
        # without being after that statement
        # A higher return value is better - the expression will appear
        # earlier in the list of values and is less likely to be trimmed
        nodes, _value = expression

        def start(n):
            # type: (ast.expr) -> Tuple[int, int]
            return (n.lineno, n.col_offset)

        nodes_before_stmt = [
            node for node in nodes if start(node) < stmt.last_token.end
        ]
        if nodes_before_stmt:
            # The position of the last node before or in the statement
            return max(start(node) for node in nodes_before_stmt)
        else:
            # The position of the first node after the statement
            # Negative means it's always lower priority than nodes that come before
            # Less negative means closer to the statement and higher priority
            lineno, col_offset = min(start(node) for node in nodes)
            return (-lineno, -col_offset)