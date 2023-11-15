    async def send(self, request: Request, timeout: Timeout = None) -> Response:
        timeout = Timeout() if timeout is None else timeout

        if not self.init_started:
            # The very first stream is responsible for initiating the connection.
            self.init_started = True
            await self.send_connection_init(timeout)
            stream_id = self.state.get_next_available_stream_id()
            self.init_complete.set()
        else:
            # All other streams need to wait until the connection is established.
            await self.init_complete.wait()
            stream_id = self.state.get_next_available_stream_id()

        stream = HTTP2Stream(stream_id=stream_id, connection=self)
        self.streams[stream_id] = stream
        self.events[stream_id] = []
        return await stream.send(request, timeout)