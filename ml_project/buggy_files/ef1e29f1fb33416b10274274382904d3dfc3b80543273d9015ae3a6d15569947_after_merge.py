def status(extra_status=''):
    """Kite completions status: not installed, ready, not running."""
    kite_installed, _ = check_if_kite_installed()
    if not kite_installed:
        return NOT_INSTALLED + extra_status
    elif check_if_kite_running():
        return RUNNING + extra_status
    else:
        return NOT_RUNNING + extra_status