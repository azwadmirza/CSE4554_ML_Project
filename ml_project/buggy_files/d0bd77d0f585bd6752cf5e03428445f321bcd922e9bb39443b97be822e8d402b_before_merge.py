def pure_eval_frame(frame):
    # type: (FrameType) -> Dict[str, Any]
    source = executing.Source.for_frame(frame)
    if not source.tree:
        return {}

    statements = source.statements_at_line(frame.f_lineno)
    if not statements:
        return {}

    scope = stmt = list(statements)[0]
    while True:
        # Get the parent first in case the original statement is already
        # a function definition, e.g. if we're calling a decorator
        # In that case we still want the surrounding scope, not that function
        scope = scope.parent
        if isinstance(scope, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            break

    evaluator = pure_eval.Evaluator.from_frame(frame)
    expressions = evaluator.interesting_expressions_grouped(scope)

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

    # This adds the first_token and last_token attributes to nodes
    atok = source.asttokens()

    expressions.sort(key=closeness, reverse=True)
    return {
        atok.get_text(nodes[0]): value
        for nodes, value in expressions[: serializer.MAX_DATABAG_BREADTH]
    }