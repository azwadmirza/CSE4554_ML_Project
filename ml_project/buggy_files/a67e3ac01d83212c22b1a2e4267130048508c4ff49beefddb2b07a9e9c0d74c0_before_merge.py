def concat_string(node, stop=None):
    '''Builds a string from a ast.BinOp chain.

    This will build a string from a series of ast.Str nodes wrapped in
    ast.BinOp nodes. Something like "a" + "b" + "c" or "a %s" % val etc.
    The provided node can be any participant in the BinOp chain.

    :param node: (ast.Str or ast.BinOp) The node to process
    :param stop: (ast.Str or ast.BinOp) Optional base node to stop at
    :returns: (Tuple) the root node of the expression, the string value
    '''
    def _get(node, bits, stop=None):
        if node != stop:
            bits.append(
                _get(node.left, bits, stop)
                if isinstance(node.left, ast.BinOp)
                else node.left)
            bits.append(
                _get(node.right, bits, stop)
                if isinstance(node.right, ast.BinOp)
                else node.right)

    bits = [node]
    while isinstance(node.parent, ast.BinOp):
        node = node.parent
    if isinstance(node, ast.BinOp):
        _get(node, bits, stop)
    return (node, " ".join([x.s for x in bits if isinstance(x, ast.Str)]))