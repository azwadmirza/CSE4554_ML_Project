    async def disconnect(self, reason: DisconnectReason) -> None:
        """
        Send a Disconnect msg to the remote peer and stop ourselves.
        """
        self.disconnect_nowait(reason)

        await self.manager.stop()