    async def _create_socket(self, server_id, data):
        async with self._handshake_check:
            if self._handshaking:
                log.info("Ignoring voice server update while handshake is in progress")
                return
            self._handshaking = True

        self._connected.clear()
        self.session_id = self.main_ws.session_id
        self.server_id = server_id
        self.token = data.get('token')
        endpoint = data.get('endpoint')

        if endpoint is None or self.token is None:
            log.warning('Awaiting endpoint... This requires waiting. ' \
                        'If timeout occurred considering raising the timeout and reconnecting.')
            return

        self.endpoint = endpoint.replace(':80', '')
        self.endpoint_ip = socket.gethostbyname(self.endpoint)

        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)

        if self._handshake_complete.is_set():
            # terminate the websocket and handle the reconnect loop if necessary.
            self._handshake_complete.clear()
            self._handshaking = False
            await self.ws.close(4000)
            return

        self._handshake_complete.set()