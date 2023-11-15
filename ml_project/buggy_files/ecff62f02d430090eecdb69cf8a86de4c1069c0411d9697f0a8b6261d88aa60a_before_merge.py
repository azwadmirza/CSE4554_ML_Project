    def closeness(expression):
        # type: (Tuple[List[Any], Any]) -> int
        # Prioritise expressions with a node closer to the statement executed
        # without being after that statement
        # A higher return value is better - the expression will appear
        # earlier in the list of values and is less likely to be trimmed
        nodes, _value = expression
        nodes_before_stmt = [
            node for node in nodes if node.first_token.startpos < stmt.last_token.endpos
        ]
        if nodes_before_stmt:
            # The position of the last node before or in the statement
            return max(node.first_token.startpos for node in nodes_before_stmt)
        else:
            # The position of the first node after the statement
            # Negative means it's always lower priority than nodes that come before
            # Less negative means closer to the statement and higher priority
            return -min(node.first_token.startpos for node in nodes)