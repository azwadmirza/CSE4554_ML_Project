    def _reconfigure(self) -> None:
        """
        Cleans up current freqtradebot instance, reloads the configuration and
        replaces it with the new instance
        """
        # Tell systemd that we initiated reconfiguration
        if self._sd_notify:
            logger.debug("sd_notify: RELOADING=1")
            self._sd_notify.notify("RELOADING=1")

        # Clean up current freqtrade modules
        self.freqtrade.cleanup()

        # Load and validate config and create new instance of the bot
        self._init(True)

        self.freqtrade.rpc.send_msg({
            'type': RPCMessageType.STATUS_NOTIFICATION,
            'status': 'config reloaded'
        })

        # Tell systemd that we completed reconfiguration
        if self._sd_notify:
            logger.debug("sd_notify: READY=1")
            self._sd_notify.notify("READY=1")