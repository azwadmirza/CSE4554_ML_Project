def _set_debug_level(self, debug_level):
    """
    :type debug_level: int, between 0-2
    :param debug_level: configure verbosity of log
    """
    mapping = {
        0: logging.ERROR,
        1: logging.INFO,
        2: logging.DEBUG,
    }

    self.setLevel(mapping[debug_level])