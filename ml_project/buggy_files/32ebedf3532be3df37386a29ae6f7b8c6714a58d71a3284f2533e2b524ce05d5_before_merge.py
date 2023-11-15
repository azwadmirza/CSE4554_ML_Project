def find_isinstance_check(node: Expression,
                          type_map: Dict[Expression, Type],
                          ) -> Tuple[TypeMap, TypeMap]:
    """Find any isinstance checks (within a chain of ands).  Includes
    implicit and explicit checks for None.

    Return value is a map of variables to their types if the condition
    is true and a map of variables to their types if the condition is false.

    If either of the values in the tuple is None, then that particular
    branch can never occur.

    Guaranteed to not return None, None. (But may return {}, {})
    """
    if isinstance(node, CallExpr):
        if refers_to_fullname(node.callee, 'builtins.isinstance'):
            expr = node.args[0]
            if expr.literal == LITERAL_TYPE:
                vartype = type_map[expr]
                type = get_isinstance_type(node.args[1], type_map)
                return conditional_type_map(expr, vartype, type)
    elif (isinstance(node, ComparisonExpr) and any(is_literal_none(n) for n in node.operands) and
          experiments.STRICT_OPTIONAL):
        # Check for `x is None` and `x is not None`.
        is_not = node.operators == ['is not']
        if is_not or node.operators == ['is']:
            if_vars = {}  # type: Dict[Expression, Type]
            else_vars = {}  # type: Dict[Expression, Type]
            for expr in node.operands:
                if expr.literal == LITERAL_TYPE and not is_literal_none(expr) and expr in type_map:
                    # This should only be true at most once: there should be
                    # two elements in node.operands, and at least one of them
                    # should represent a None.
                    vartype = type_map[expr]
                    if_vars, else_vars = conditional_type_map(expr, vartype, NoneTyp())
                    break

            if is_not:
                if_vars, else_vars = else_vars, if_vars
            return if_vars, else_vars
    elif isinstance(node, RefExpr):
        # Restrict the type of the variable to True-ish/False-ish in the if and else branches
        # respectively
        vartype = type_map[node]
        if_type = true_only(vartype)
        else_type = false_only(vartype)
        ref = node  # type: Expression
        if_map = {ref: if_type} if not isinstance(if_type, UninhabitedType) else None
        else_map = {ref: else_type} if not isinstance(else_type, UninhabitedType) else None
        return if_map, else_map
    elif isinstance(node, OpExpr) and node.op == 'and':
        left_if_vars, left_else_vars = find_isinstance_check(node.left, type_map)
        right_if_vars, right_else_vars = find_isinstance_check(node.right, type_map)

        # (e1 and e2) is true if both e1 and e2 are true,
        # and false if at least one of e1 and e2 is false.
        return (and_conditional_maps(left_if_vars, right_if_vars),
                or_conditional_maps(left_else_vars, right_else_vars))
    elif isinstance(node, OpExpr) and node.op == 'or':
        left_if_vars, left_else_vars = find_isinstance_check(node.left, type_map)
        right_if_vars, right_else_vars = find_isinstance_check(node.right, type_map)

        # (e1 or e2) is true if at least one of e1 or e2 is true,
        # and false if both e1 and e2 are false.
        return (or_conditional_maps(left_if_vars, right_if_vars),
                and_conditional_maps(left_else_vars, right_else_vars))
    elif isinstance(node, UnaryExpr) and node.op == 'not':
        left, right = find_isinstance_check(node.expr, type_map)
        return right, left

    # Not a supported isinstance check
    return {}, {}