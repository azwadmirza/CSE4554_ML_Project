def _is_background_tty():
    """Return True iff this process is backgrounded and stdout is a tty"""
    if sys.stdout.isatty():
        return os.getpgrp() != os.tcgetpgrp(sys.stdout.fileno())
    return False  # not writing to tty, not background