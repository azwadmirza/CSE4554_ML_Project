    async def send(self, request: Request, timeout: Timeout = None) -> Response:
        timeout = Timeout() if timeout is None else timeout

        async with self.init_lock:
            if not self.sent_connection_init:
                # The very first stream is responsible for initiating the connection.
                await self.send_connection_init(timeout)
                self.sent_connection_init = True
            stream_id = self.state.get_next_available_stream_id()

        stream = HTTP2Stream(stream_id=stream_id, connection=self)
        self.streams[stream_id] = stream
        self.events[stream_id] = []
        return await stream.send(request, timeout)