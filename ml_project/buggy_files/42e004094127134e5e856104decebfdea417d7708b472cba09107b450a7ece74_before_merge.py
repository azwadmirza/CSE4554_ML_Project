    async def listen(self):
        """Listen for and parse new messages."""
        while self.listening:
            await self.receive_from_websocket()