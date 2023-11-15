def repr_domxml(node, length=80):
    # type: (nodes.Node, Optional[int]) -> unicode
    """
    return DOM XML representation of the specified node like:
    '<paragraph translatable="False"><inline classes="versionmodified">New in version...'

    :param nodes.Node node: target node
    :param int length:
       length of return value to be striped. if false-value is specified, repr_domxml
       returns full of DOM XML representation.
    :return: DOM XML representation
    """
    try:
        text = node.asdom().toxml()
    except Exception:
        text = text_type(node)
    if length and len(text) > length:
        text = text[:length] + '...'
    return text