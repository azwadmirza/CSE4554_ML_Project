def _get_bug_attr(bug, attr):
    """Default only the longdescs case to [] since it may not be present."""
    if attr == "longdescs":
        return getattr(bug, attr, [])
    return getattr(bug, attr)