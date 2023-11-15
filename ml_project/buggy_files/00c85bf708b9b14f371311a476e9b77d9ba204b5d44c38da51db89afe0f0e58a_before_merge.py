def hy_compile(tree, module_name, root=ast.Module, get_expr=False):
    """
    Compile a HyObject tree into a Python AST Module.

    If `get_expr` is True, return a tuple (module, last_expression), where
    `last_expression` is the.
    """

    body = []
    expr = None

    if not (isinstance(tree, HyObject) or type(tree) is list):
        raise HyCompileError("tree must be a HyObject or a list")

    if isinstance(tree, HyObject) or tree:
        compiler = HyASTCompiler(module_name)
        result = compiler.compile(tree)
        expr = result.force_expr

        if not get_expr:
            result += result.expr_as_stmt()

        # We need to test that the type is *exactly* `list` because we don't
        # want to do `tree[0]` on HyList or such.
        spoof_tree = tree[0] if type(tree) is list else tree
        body = compiler.imports_as_stmts(spoof_tree) + result.stmts

    ret = root(body=body)

    if get_expr:
        expr = ast.Expression(body=expr)
        ret = (ret, expr)

    return ret