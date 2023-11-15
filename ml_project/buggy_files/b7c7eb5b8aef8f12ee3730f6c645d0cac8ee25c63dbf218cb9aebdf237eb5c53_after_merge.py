    async def asgi_receive(self):
        if not self.connect_sent:
            self.connect_sent = True
            return {"type": "websocket.connect"}

        await self.handshake_completed_event.wait()
        try:
            await self.ensure_open()
            data = await self.recv()
        except websockets.ConnectionClosed as exc:
            return {"type": "websocket.disconnect", "code": exc.code}

        msg = {"type": "websocket.receive"}

        if isinstance(data, str):
            msg["text"] = data
        else:
            msg["bytes"] = data

        return msg