def pid_exists(pid):
    """Check For the existence of a unix pid."""
    return _psposix.pid_exists(pid)