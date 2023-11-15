def _is_node_return_ended(node):
    """Check if the node ends with an explicit return statement.

    Args:
        node (astroid.NodeNG): node to be checked.

    Returns:
        bool: True if the node ends with an explicit statement, False otherwise.

    """
    # Recursion base case
    if isinstance(node, astroid.Return):
        return True
    if isinstance(node, astroid.Raise):
        # a Raise statement doesn't need to end with a return statement
        # but if the exception raised is handled, then the handler has to
        # ends with a return statement
        exc = utils.safe_infer(node.exc)
        if exc is None or exc is astroid.Uninferable:
            return False
        exc_name = exc.pytype().split('.')[-1]
        handlers = utils.get_exception_handlers(node, exc_name)
        if handlers:
            # among all the handlers handling the exception at least one
            # must end with a return statement
            return any(_is_node_return_ended(_handler) for _handler in handlers)
        # if no handlers handle the exception then it's ok
        return True
    if isinstance(node, astroid.If):
        # if statement is returning if there are exactly two return statements in its
        # children : one for the body part, the other for the orelse part
        return_stmts = [_is_node_return_ended(_child) for _child in node.get_children()]
        return sum(return_stmts) == 2
    # recurses on the children of the node except for those which are except handler
    # because one cannot be sure that the handler will really be used
    return any(_is_node_return_ended(_child) for _child in node.get_children()
               if not isinstance(_child, astroid.ExceptHandler))