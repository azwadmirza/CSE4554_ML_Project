def is_default_argument(node: astroid.node_classes.NodeNG) -> bool:
    """return true if the given Name node is used in function or lambda
    default argument's value
    """
    parent = node.scope()
    if isinstance(parent, (astroid.FunctionDef, astroid.Lambda)):
        for default_node in parent.args.defaults:
            for default_name_node in default_node.nodes_of_class(astroid.Name):
                if default_name_node is node:
                    return True
    return False