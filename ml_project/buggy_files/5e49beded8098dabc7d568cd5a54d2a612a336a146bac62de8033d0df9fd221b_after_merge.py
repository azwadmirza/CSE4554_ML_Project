    async def send(self, message):
        await self.writable.wait()

        message_type = message["type"]

        if not self.handshake_complete:
            if message_type == "websocket.accept":
                self.logger.info(
                    '%s - "WebSocket %s" [accepted]',
                    self.scope["client"],
                    self.scope["root_path"] + self.scope["path"],
                )
                self.handshake_complete = True
                subprotocol = message.get("subprotocol")
                output = self.conn.send(
                    wsproto.events.AcceptConnection(
                        subprotocol=subprotocol, extensions=[PerMessageDeflate()]
                    )
                )
                self.transport.write(output)

            elif message_type == "websocket.close":
                self.queue.put_nowait({"type": "websocket.disconnect", "code": None})
                self.logger.info(
                    '%s - "WebSocket %s" 403',
                    self.scope["client"],
                    self.scope["root_path"] + self.scope["path"],
                )
                self.handshake_complete = True
                self.close_sent = True
                msg = events.RejectConnection(status_code=403, headers=[])
                output = self.conn.send(msg)
                self.transport.write(output)
                self.transport.close()

            else:
                msg = (
                    "Expected ASGI message 'websocket.accept' or 'websocket.close', "
                    "but got '%s'."
                )
                raise RuntimeError(msg % message_type)

        elif not self.close_sent:
            if message_type == "websocket.send":
                bytes_data = message.get("bytes")
                text_data = message.get("text")
                data = text_data if bytes_data is None else bytes_data
                output = self.conn.send(wsproto.events.Message(data=data))
                if not self.transport.is_closing():
                    self.transport.write(output)

            elif message_type == "websocket.close":
                self.close_sent = True
                code = message.get("code", 1000)
                self.queue.put_nowait({"type": "websocket.disconnect", "code": code})
                output = self.conn.send(wsproto.events.CloseConnection(code=code))
                if not self.transport.is_closing():
                    self.transport.write(output)
                    self.transport.close()

            else:
                msg = (
                    "Expected ASGI message 'websocket.send' or 'websocket.close',"
                    " but got '%s'."
                )
                raise RuntimeError(msg % message_type)

        else:
            msg = "Unexpected ASGI message '%s', after sending 'websocket.close'."
            raise RuntimeError(msg % message_type)