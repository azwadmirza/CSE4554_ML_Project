def attr_attributes_transform(node):
    """Given that the ClassNode has an attr decorator,
    rewrite class attributes as instance attributes
    """
    for cdefbodynode in node.body:
        if not isinstance(cdefbodynode, astroid.Assign):
            continue
        for target in cdefbodynode.targets:
            node.locals[target.name] = [astroid.Attribute(target.name)]