def get_posonlyargs(node: AnyFunctionDefAndLambda) -> List[ast.arg]:
    """
    Helper function to get posonlyargs in all version of python.

    This field was added in ``python3.8+``. And it was not present before.

    mypy also gives an error on this on older version of python::

        error: "arguments" has no attribute "posonlyargs"; maybe "kwonlyargs"?

    """
    return getattr(node.args, 'posonlyargs', [])