    async def connect(self):
        log.info('WebSocket connection opened')

        subprotocols = self.scope["subprotocols"]
        if len(subprotocols) != 2 or subprotocols[0] != 'bokeh':
            self.close()
            raise RuntimeError("Subprotocol header is not 'bokeh'")

        token = subprotocols[1]
        if token is None:
            self.close()
            raise RuntimeError("No token received in subprotocol header")

        now = calendar.timegm(dt.datetime.now().utctimetuple())
        payload = get_token_payload(token)
        if 'session_expiry' not in payload:
            self.close()
            raise RuntimeError("Session expiry has not been provided")
        elif now >= payload['session_expiry']:
            self.close()
            raise RuntimeError("Token is expired.")
        elif not check_token_signature(token,
                                       signed=False,
                                       secret_key=None):
            session_id = get_session_id(token)
            log.error("Token for session %r had invalid signature", session_id)
            raise RuntimeError("Invalid token signature")

        def on_fully_opened(future):
            e = future.exception()
            if e is not None:
                # this isn't really an error (unless we have a
                # bug), it just means a client disconnected
                # immediately, most likely.
                log.debug("Failed to fully open connlocksection %r", e)

        future = self._async_open(token)

        # rewrite above line using asyncio
        # this task is scheduled to run soon once context is back to event loop
        task = asyncio.ensure_future(future)
        task.add_done_callback(on_fully_opened)
        await self.accept("bokeh")