    async def stop(self):
        if self._web_socket_available():
            self.exchange_web_socket.stop_sockets()
        await self.exchange.stop()