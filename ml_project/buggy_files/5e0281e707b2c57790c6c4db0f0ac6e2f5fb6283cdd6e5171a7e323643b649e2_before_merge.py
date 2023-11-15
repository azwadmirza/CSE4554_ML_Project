def validate_expression(expr, variable_set, function_set=[], names=None):
    global last_func
    names = names if names is not None else []
    if isinstance(expr, six.string_types):
        node = ast.parse(expr)
        if len(node.body) != 1:
            raise ValueError("expected one expression, got %r" %
                             len(node.body))
        first_expr = node.body[0]
        if not isinstance(first_expr, _ast.Expr):
            raise ValueError("expected an expression got a %r" %
                             type(node.body))
        validate_expression(first_expr.value, variable_set,
                            function_set, names)
    elif isinstance(expr, _ast.BinOp):
        if expr.op.__class__ in valid_binary_operators:
            validate_expression(expr.right, variable_set, function_set, names)
            validate_expression(expr.left, variable_set, function_set, names)
        else:
            raise ValueError("Binary operator not allowed: %r" % expr.op)
    elif isinstance(expr, _ast.UnaryOp):
        if expr.op.__class__ in valid_unary_operators:
            validate_expression(expr.operand, variable_set,
                                function_set, names)
        else:
            raise ValueError("Unary operator not allowed: %r" % expr.op)
    elif isinstance(expr, _ast.Name):
        validate_id(expr.id)
        if expr.id not in variable_set:
            matches = difflib.get_close_matches(expr.id, list(variable_set))
            msg = "Column or variable %r does not exist." % expr.id
            if matches:
                msg += ' Did you mean: ' + " or ".join(map(repr, matches))

            raise NameError(msg)
        names.append(expr.id)
    elif isinstance(expr, ast_Num):
        pass  # numbers are fine
    elif isinstance(expr, ast_Str):
        pass  # as well as strings
    elif isinstance(expr, _ast.Call):
        validate_func(expr.func, function_set)
        last_func = expr
        for arg in expr.args:
            validate_expression(arg, variable_set, function_set, names)
        for arg in expr.keywords:
            validate_expression(arg, variable_set, function_set, names)
    elif isinstance(expr, _ast.Compare):
        validate_expression(expr.left, variable_set, function_set, names)
        for op in expr.ops:
            if op.__class__ not in valid_compare_operators:
                raise ValueError("Compare operator not allowed: %r" % op)
        for comparator in expr.comparators:
            validate_expression(comparator, variable_set, function_set, names)
    elif isinstance(expr, _ast.keyword):
        validate_expression(expr.value, variable_set, function_set, names)
    elif isinstance(expr, ast_Constant):
        pass  # like True and False
    elif isinstance(expr, _ast.Subscript):
        validate_expression(expr.value, variable_set, function_set, names)
        if isinstance(expr.slice.value, ast_Num):
            pass  # numbers are fine
        elif isinstance(expr.slice.value, _ast.Str):
            pass  # and strings
        else:
            raise ValueError(
                "Only subscript/slices with numbers allowed, not: %r" % expr.slice.value)
    else:
        last_func = expr
        raise ValueError("Unknown expression type: %r" % type(expr))