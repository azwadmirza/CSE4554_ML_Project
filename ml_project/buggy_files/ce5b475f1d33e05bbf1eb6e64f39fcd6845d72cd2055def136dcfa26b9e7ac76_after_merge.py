    async def _read_messages(self):
        """Process messages received on the WebSocket connection."""
        text_message_callback_executions: List[Future] = []
        while not self._stopped and self._websocket is not None:
            for future in text_message_callback_executions:
                if future.done():
                    text_message_callback_executions.remove(future)

            try:
                # Wait for a message to be received, but timeout after a second so that
                # we can check if the socket has been closed, or if self._stopped is
                # True
                message = await self._websocket.receive(timeout=1)
            except asyncio.TimeoutError:
                if not self._websocket.closed:
                    # We didn't receive a message within the timeout interval, but
                    # aiohttp hasn't closed the socket, so ping responses must still be
                    # returning
                    continue
                self._logger.warning(
                    "Websocket was closed (%s).", self._websocket.close_code
                )
                await self._dispatch_event(
                    event="error", data=self._websocket.exception()
                )
                self._websocket = None
                await self._dispatch_event(event="close")
                num_of_running_callbacks = len(text_message_callback_executions)
                if num_of_running_callbacks > 0:
                    self._logger.info(
                        "WebSocket connection has been closed "
                        f"though {num_of_running_callbacks} callback executions were still in progress"
                    )
                return

            if message.type == aiohttp.WSMsgType.TEXT:
                payload = message.json()
                event = payload.pop("type", "Unknown")

                async def run_dispatch_event():
                    try:
                        await self._dispatch_event(event, data=payload)
                    except Exception as err:
                        data = message.data if message else message
                        self._logger.info(
                            f"Caught a raised exception ({err}) while dispatching a TEXT message ({data})"
                        )
                        # Raised exceptions here happen in users' code and were just unhandled.
                        # As they're not intended for closing current WebSocket connection,
                        # this exception should not be propagated to higher level (#_connect_and_read()).
                        return

                # Asynchronously run callbacks to handle simultaneous incoming messages from Slack
                f = asyncio.ensure_future(run_dispatch_event())
                text_message_callback_executions.append(f)
            elif message.type == aiohttp.WSMsgType.ERROR:
                self._logger.error("Received an error on the websocket: %r", message)
                await self._dispatch_event(event="error", data=message)
            elif message.type in (
                aiohttp.WSMsgType.CLOSE,
                aiohttp.WSMsgType.CLOSING,
                aiohttp.WSMsgType.CLOSED,
            ):
                self._logger.warning("Websocket was closed.")
                self._websocket = None
                await self._dispatch_event(event="close")
            else:
                self._logger.debug("Received unhandled message type: %r", message)