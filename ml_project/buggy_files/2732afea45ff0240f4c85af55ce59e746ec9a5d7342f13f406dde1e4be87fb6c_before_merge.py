    async def _connect_and_read(self):
        """Retreives the WS url and connects to Slack's RTM API.

        Makes an authenticated call to Slack's Web API to retrieve
        a websocket URL. Then connects to the message server and
        reads event messages as they come in.

        If 'auto_reconnect' is specified we
        retrieve a new url and reconnect any time the connection
        is lost unintentionally or an exception is thrown.

        Raises:
            SlackApiError: Unable to retreive RTM URL from Slack.
            websockets.exceptions: Errors thrown by the 'websockets' library.
        """
        while not self._stopped:
            try:
                self._connection_attempts += 1
                async with aiohttp.ClientSession(
                    loop=self._event_loop,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as session:
                    self._session = session
                    url, data = await self._retreive_websocket_info()
                    async with session.ws_connect(
                        url,
                        heartbeat=self.ping_interval,
                        ssl=self.ssl,
                        proxy=self.proxy,
                    ) as websocket:
                        self._logger.debug("The Websocket connection has been opened.")
                        self._websocket = websocket
                        await self._dispatch_event(event="open", data=data)
                        await self._read_messages()
                        # The websocket has been disconnected, or self._stopped is True
                        if not self._stopped and not self.auto_reconnect:
                            self._logger.warning(
                                "Not reconnecting the Websocket because auto_reconnect is False"
                            )
                            return
                        # No need to wait exponentially here, since the connection was
                        # established OK, but timed out, or was closed remotely
            except (
                client_err.SlackClientNotConnectedError,
                client_err.SlackApiError,
                # TODO: Catch websocket exceptions thrown by aiohttp.
            ) as exception:
                self._logger.debug(str(exception))
                await self._dispatch_event(event="error", data=exception)
                if self.auto_reconnect and not self._stopped:
                    await self._wait_exponentially(exception)
                    continue
                self._logger.exception(
                    "The Websocket encountered an error. Closing the connection..."
                )
                self._close_websocket()
                raise