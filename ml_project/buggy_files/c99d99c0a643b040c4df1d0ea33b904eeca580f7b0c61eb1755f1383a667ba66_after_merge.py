    def open(self):
        ''' Initialize a connection to a client.

        Returns:
            None

        '''
        log.info('WebSocket connection opened')

        proto_version = self.get_argument("bokeh-protocol-version", default=None)
        if proto_version is None:
            self.close()
            raise ProtocolError("No bokeh-protocol-version specified")

        session_id = self.get_argument("bokeh-session-id", default=None)
        if session_id is None:
            self.close()
            raise ProtocolError("No bokeh-session-id specified")

        if not check_session_id_signature(session_id,
                                          signed=self.application.sign_sessions,
                                          secret_key=self.application.secret_key):
            log.error("Session id had invalid signature: %r", session_id)
            raise ProtocolError("Invalid session ID")

        def on_fully_opened(future):
            e = future.exception()
            if e is not None:
                # this isn't really an error (unless we have a
                # bug), it just means a client disconnected
                # immediately, most likely.
                log.debug("Failed to fully open connection %r", e)

        future = self._async_open(session_id, proto_version)
        self.application.io_loop.add_future(future, on_fully_opened)