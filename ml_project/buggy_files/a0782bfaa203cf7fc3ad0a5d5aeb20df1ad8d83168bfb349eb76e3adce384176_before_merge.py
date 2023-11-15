def const_factory(value):
    """return an astroid node for a python value"""
    # XXX we should probably be stricter here and only consider stuff in
    # CONST_CLS or do better treatment: in case where value is not in CONST_CLS,
    # we should rather recall the builder on this value than returning an empty
    # node (another option being that const_factory shouldn't be called with something
    # not in CONST_CLS)
    assert not isinstance(value, bases.NodeNG)
    try:
        return CONST_CLS[value.__class__](value)
    except (KeyError, AttributeError):
        node = EmptyNode()
        node.object = value
        return node