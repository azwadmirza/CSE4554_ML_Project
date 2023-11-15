    async def asgi_send(self, message):
        message_type = message["type"]

        if not self.handshake_started_event.is_set():
            if message_type == "websocket.accept":
                self.logger.info(
                    '%s - "WebSocket %s" [accepted]',
                    self.scope["client"],
                    self.scope["root_path"] + self.scope["path"],
                )
                self.initial_response = None
                self.accepted_subprotocol = message.get("subprotocol")
                self.handshake_started_event.set()

            elif message_type == "websocket.close":
                self.logger.info(
                    '%s - "WebSocket %s" 403',
                    self.scope["client"],
                    self.scope["root_path"] + self.scope["path"],
                )
                self.initial_response = (http.HTTPStatus.FORBIDDEN, [], b"")
                self.handshake_started_event.set()
                self.closed_event.set()

            else:
                msg = (
                    "Expected ASGI message 'websocket.accept' or 'websocket.close', "
                    "but got '%s'."
                )
                raise RuntimeError(msg % message_type)

        elif not self.closed_event.is_set():
            await self.handshake_completed_event.wait()

            if message_type == "websocket.send":
                bytes_data = message.get("bytes")
                text_data = message.get("text")
                data = text_data if bytes_data is None else bytes_data
                await self.send(data)

            elif message_type == "websocket.close":
                code = message.get("code", 1000)
                await self.close(code)
                self.closed_event.set()

            else:
                msg = (
                    "Expected ASGI message 'websocket.send' or 'websocket.close',"
                    " but got '%s'."
                )
                raise RuntimeError(msg % message_type)

        else:
            msg = "Unexpected ASGI message '%s', after sending 'websocket.close'."
            raise RuntimeError(msg % message_type)