    async def listen(self):
        """Listen for and parse new messages."""
        while self.listening:
            try:
                await self.receive_from_websocket()
            except AttributeError:
                break