def hy_compile(tree, module_name, root=ast.Module, get_expr=False):
    """
    Compile a HyObject tree into a Python AST Module.

    If `get_expr` is True, return a tuple (module, last_expression), where
    `last_expression` is the.
    """

    body = []
    expr = None

    if not isinstance(tree, HyObject):
        tree = wrap_value(tree)
        if not isinstance(tree, HyObject):
            raise HyCompileError("`tree` must be a HyObject or capable of "
                                 "being promoted to one")
        spoof_positions(tree)

    compiler = HyASTCompiler(module_name)
    result = compiler.compile(tree)
    expr = result.force_expr

    if not get_expr:
        result += result.expr_as_stmt()

    body = compiler.imports_as_stmts(tree) + result.stmts

    ret = root(body=body)

    if get_expr:
        expr = ast.Expression(body=expr)
        ret = (ret, expr)

    return ret