def status():
    """Kite completions status: not installed, ready, not running."""
    kite_installed, _ = check_if_kite_installed()
    if not kite_installed:
        return NOT_INSTALLED
    elif check_if_kite_running():
        return RUNNING
    else:
        return NOT_RUNNING