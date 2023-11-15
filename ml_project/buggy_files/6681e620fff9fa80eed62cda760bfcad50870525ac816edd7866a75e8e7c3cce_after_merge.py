def _is_background_tty(stream):
    """True if the stream is a tty and calling process is in the background.
    """
    return (
        stream.isatty() and
        os.getpgrp() != os.tcgetpgrp(stream.fileno())
    )