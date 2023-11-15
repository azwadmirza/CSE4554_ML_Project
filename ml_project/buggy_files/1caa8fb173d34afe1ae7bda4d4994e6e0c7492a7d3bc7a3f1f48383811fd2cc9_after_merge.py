def _get_bug_attr(bug, attr):
    """Default longdescs/flags case to [] since they may not be present."""
    if attr in ("longdescs", "flags"):
        return getattr(bug, attr, [])
    return getattr(bug, attr)