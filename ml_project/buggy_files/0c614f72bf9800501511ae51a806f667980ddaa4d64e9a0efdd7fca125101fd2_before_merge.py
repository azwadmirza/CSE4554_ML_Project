    def open(self):
        ''' Initialize a connection to a client.

        Returns:
            None

        '''
        log.info('WebSocket connection opened')
        token = self._token

        if self.selected_subprotocol != 'bokeh':
            self.close()
            raise ProtocolError("Subprotocol header is not 'bokeh'")
        elif token is None:
            self.close()
            raise ProtocolError("No token received in subprotocol header")

        now = calendar.timegm(dt.datetime.now().utctimetuple())
        payload = get_token_payload(token)
        if 'session_expiry' not in payload:
            self.close()
            raise ProtocolError("Session expiry has not been provided")
        elif now >= payload['session_expiry']:
            self.close()
            raise ProtocolError("Token is expired.")
        elif not check_token_signature(token,
                                       signed=self.application.sign_sessions,
                                       secret_key=self.application.secret_key):
            session_id = get_session_id(token)
            log.error("Token for session %r had invalid signature", session_id)
            raise ProtocolError("Invalid token signature")

        try:
            self.application.io_loop.spawn_callback(self._async_open, self._token)
        except Exception as e:
            # this isn't really an error (unless we have a
            # bug), it just means a client disconnected
            # immediately, most likely.
            log.debug("Failed to fully open connection %r", e)