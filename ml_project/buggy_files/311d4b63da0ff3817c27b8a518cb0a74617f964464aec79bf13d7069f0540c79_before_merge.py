def _evaluate_ast(node):
    wrapper = None
    statement = ''

    if isinstance(node.parent, ast.BinOp):
        out = utils.concat_string(node, node.parent)
        wrapper = out[0].parent
        statement = out[1]
    elif (isinstance(node.parent, ast.Attribute)
          and node.parent.attr == 'format'):
        statement = node.s
        # Hierarchy for "".format() is Wrapper -> Call -> Attribute -> Str
        wrapper = node.parent.parent.parent
    elif hasattr(ast, 'JoinedStr') and isinstance(node.parent, ast.JoinedStr):
        statement = node.s
        wrapper = node.parent.parent

    if isinstance(wrapper, ast.Call):  # wrapped in "execute" call?
        names = ['execute', 'executemany']
        name = utils.get_called_name(wrapper)
        return (name in names, statement)
    else:
        return (False, statement)