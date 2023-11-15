def _evaluate_ast(node):
    wrapper = None
    statement = ''

    if isinstance(node._bandit_parent, ast.BinOp):
        out = utils.concat_string(node, node._bandit_parent)
        wrapper = out[0]._bandit_parent
        statement = out[1]
    elif (isinstance(node._bandit_parent, ast.Attribute)
          and node._bandit_parent.attr == 'format'):
        statement = node.s
        # Hierarchy for "".format() is Wrapper -> Call -> Attribute -> Str
        wrapper = node._bandit_parent._bandit_parent._bandit_parent
    elif (hasattr(ast, 'JoinedStr')
          and isinstance(node._bandit_parent, ast.JoinedStr)):
        statement = node.s
        wrapper = node._bandit_parent._bandit_parent

    if isinstance(wrapper, ast.Call):  # wrapped in "execute" call?
        names = ['execute', 'executemany']
        name = utils.get_called_name(wrapper)
        return (name in names, statement)
    else:
        return (False, statement)