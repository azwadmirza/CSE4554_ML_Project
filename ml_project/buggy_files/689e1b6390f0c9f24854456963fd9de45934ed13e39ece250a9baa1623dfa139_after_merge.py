def transform2call(var):
    if isinstance(var, ast.BinOp):
        is_mod = isinstance(var.op, ast.Mod)
        is_left_str = isinstance(var.left, ast.Str)
        if is_mod and is_left_str:
            new_call = ast.Call()
            new_call.args = []
            new_call.args = []
            if six.PY2:
                new_call.starargs = None
            new_call.keywords = None
            if six.PY2:
                new_call.kwargs = None
            new_call.lineno = var.lineno
            new_call.func = ast.Attribute()
            new_call.func.value = var.left
            new_call.func.attr = 'format'
            if isinstance(var.right, ast.Tuple):
                new_call.args = var.right.elts
            elif six.PY2 and isinstance(var.right, ast.Dict):
                new_call.kwargs = var.right
            else:
                new_call.args = [var.right]
            return new_call