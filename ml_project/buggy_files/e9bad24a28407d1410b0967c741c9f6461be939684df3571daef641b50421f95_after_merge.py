    def onClose(self, wasClean):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onClose`
        """
        self._transport = None

        if self._session_id:

            # fire callback and close the transport
            try:
                self.onLeave(types.CloseDetails())
            except Exception:
                self.log.failure("Exception raised in onLeave callback")

            try:
                self._router.detach(self)
            except Exception as e:
                self.log.error(
                    "Failed to detach session '{}': {}".format(self._session_id, e)
                )
                self.log.debug("{tb}".format(tb=Failure().getTraceback()))

            self._session_id = None

        self._pending_session_id = None

        self._authid = None
        self._authrole = None
        self._authmethod = None
        self._authprovider = None