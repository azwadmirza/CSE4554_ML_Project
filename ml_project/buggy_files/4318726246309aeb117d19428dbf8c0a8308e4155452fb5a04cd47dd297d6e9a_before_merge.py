    async def websocket_handler(self, request):
        """Handle for aiohttp handling websocket connections."""
        socket = request.match_info.get('socket')
        available = [item for item in self.available_connections
                     if item["id"] == socket]
        if len(available) != 1:
            return aiohttp.web.Response(
                text=json.dumps("Please request a socket first"), status=400)
        if (datetime.now() - available[0]["date"]).total_seconds() \
                > self.connection_timeout:
            self.available_connections.remove(available[0])
            return aiohttp.web.Response(
                text=json.dumps("Socket request timed out"), status=408)
        self.available_connections.remove(available[0])
        _LOGGER.debug("User connected to %s", socket)

        websocket = aiohttp.web.WebSocketResponse()
        await websocket.prepare(request)

        self.active_connections[socket] = websocket

        async for msg in websocket:
            if msg.type == aiohttp.WSMsgType.TEXT:
                message = Message(None, socket, self, msg.data)
                await self.opsdroid.parse(message)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                _LOGGER.error('Websocket connection closed with exception %s',
                              websocket.exception())

        _LOGGER.info('websocket connection closed')
        self.active_connections.pop(socket, None)

        return websocket