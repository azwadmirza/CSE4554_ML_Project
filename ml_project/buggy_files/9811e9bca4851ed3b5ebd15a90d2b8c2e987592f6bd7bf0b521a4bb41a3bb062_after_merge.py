def is_default_argument(
    node: astroid.node_classes.NodeNG,
    scope: Optional[astroid.node_classes.NodeNG] = None,
) -> bool:
    """return true if the given Name node is used in function or lambda
    default argument's value
    """
    if not scope:
        scope = node.scope()
    if isinstance(scope, (astroid.FunctionDef, astroid.Lambda)):
        for default_node in scope.args.defaults:
            for default_name_node in default_node.nodes_of_class(astroid.Name):
                if default_name_node is node:
                    return True
    return False