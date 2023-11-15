    def exit(self) -> None:
        # Tell systemd that we are exiting now
        if self._sd_notify:
            logger.debug("sd_notify: STOPPING=1")
            self._sd_notify.notify("STOPPING=1")

        if self.freqtrade:
            self.freqtrade.rpc.send_msg({
                'type': RPCMessageType.STATUS_NOTIFICATION,
                'status': 'process died'
            })
            self.freqtrade.cleanup()