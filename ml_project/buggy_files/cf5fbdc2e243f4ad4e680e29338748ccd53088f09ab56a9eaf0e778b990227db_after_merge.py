    def onClose(self, wasClean, code, reason):
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onClose`
        """
        # WAMP session might never have been established in the first place .. guard this!
        self._onclose_reason = reason
        if self._session is not None:
            # WebSocket connection lost - fire off the WAMP
            # session close callback
            # noinspection PyBroadException
            try:
                self.log.debug('WAMP-over-WebSocket transport lost: wasClean={wasClean}, code={code}, reason="{reason}"', wasClean=wasClean, code=code, reason=reason)
                self._session.onClose(wasClean)
            except Exception:
                self.log.critical("{tb}", tb=traceback.format_exc())
            self._session = None