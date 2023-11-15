    async def asgi_receive(self):
        if not self.connect_sent:
            self.connect_sent = True
            return {"type": "websocket.connect"}

        await self.handshake_completed_event.wait()

        if self.closed_event.is_set():
            # If the client disconnected: WebSocketServerProtocol set self.close_code.
            # If the handshake failed or the app closed before handshake completion,
            # use 1006 Abnormal Closure.
            code = getattr(self, "close_code", 1006)
            return {"type": "websocket.disconnect", "code": code}

        try:
            data = await self.recv()
        except websockets.ConnectionClosed as exc:
            return {"type": "websocket.disconnect", "code": exc.code}

        msg = {"type": "websocket.receive"}

        if isinstance(data, str):
            msg["text"] = data
        else:
            msg["bytes"] = data

        return msg