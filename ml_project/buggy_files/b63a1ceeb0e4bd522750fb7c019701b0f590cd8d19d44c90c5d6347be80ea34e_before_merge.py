def linerange_fix(node):
    """Try and work around a known Python bug with multi-line strings."""
    # deal with multiline strings lineno behavior (Python issue #16806)
    lines = linerange(node)
    if hasattr(node, 'sibling') and hasattr(node.sibling, 'lineno'):
        start = min(lines)
        delta = node.sibling.lineno - start
        if delta > 1:
            return list(range(start, node.sibling.lineno))
    return lines