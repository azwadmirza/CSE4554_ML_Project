def attr_attributes_transform(node):
    """Given that the ClassNode has an attr decorator,
    rewrite class attributes as instance attributes
    """
    for cdefbodynode in node.body:
        if not isinstance(cdefbodynode, astroid.Assign):
            continue
        for target in cdefbodynode.targets:
            rhs_node = astroid.Unknown(
                lineno=cdefbodynode.lineno,
                col_offset=cdefbodynode.col_offset,
                parent=cdefbodynode
            )
            node.locals[target.name] = [rhs_node]