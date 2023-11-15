def check_risk(node):
    description = "Potential XSS on mark_safe function."
    xss_var = node.args[0]

    secure = False

    if isinstance(xss_var, ast.Name):
        # Check if the var are secure
        parent = node.parent
        while not isinstance(parent, (ast.Module, ast.FunctionDef)):
            parent = parent.parent

        is_param = False
        if isinstance(parent, ast.FunctionDef):
            for name in parent.args.args:
                arg_name = name.id if six.PY2 else name.arg
                if arg_name == xss_var.id:
                    is_param = True
                    break

        if not is_param:
            secure = evaluate_var(xss_var, parent, node.lineno)
    elif isinstance(xss_var, ast.Call):
        parent = node.parent
        while not isinstance(parent, (ast.Module, ast.FunctionDef)):
            parent = parent.parent
        secure = evaluate_call(xss_var, parent)
    elif isinstance(xss_var, ast.BinOp):
        is_mod = isinstance(xss_var.op, ast.Mod)
        is_left_str = isinstance(xss_var.left, ast.Str)
        if is_mod and is_left_str:
            parent = node.parent
            while not isinstance(parent, (ast.Module, ast.FunctionDef)):
                parent = parent.parent
            new_call = transform2call(xss_var)
            secure = evaluate_call(new_call, parent)

    if not secure:
        return bandit.Issue(
            severity=bandit.MEDIUM,
            confidence=bandit.HIGH,
            text=description
        )