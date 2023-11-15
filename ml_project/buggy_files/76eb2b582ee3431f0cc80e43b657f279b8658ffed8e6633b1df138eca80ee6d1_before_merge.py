    def __init__(self, args: Dict[str, Any], config=None) -> None:
        """
        Init all variables and objects the bot needs to work
        """
        logger.info('Starting worker %s', __version__)

        self._args = args
        self._config = config
        self._init(False)

        # Tell systemd that we completed initialization phase
        if self._sd_notify:
            logger.debug("sd_notify: READY=1")
            self._sd_notify.notify("READY=1")