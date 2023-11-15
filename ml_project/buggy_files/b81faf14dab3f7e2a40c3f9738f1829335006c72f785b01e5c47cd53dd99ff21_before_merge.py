def _environ_cols_tput(*_):  # pragma: no cover
    """cygwin xterm (windows)"""
    try:
        import shlex
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        # rows = int(subprocess.check_call(shlex.split('tput lines')))
        return cols
    except:
        pass
    return None