def function_type(func: mypy.nodes.FuncBase, fallback: Instance) -> FunctionLike:
    if func.type:
        assert isinstance(func.type, FunctionLike)
        return func.type
    else:
        # Implicit type signature with dynamic types.
        # Overloaded functions always have a signature, so func must be an ordinary function.
        assert isinstance(func, mypy.nodes.FuncItem), str(func)
        return callable_type(func, fallback)