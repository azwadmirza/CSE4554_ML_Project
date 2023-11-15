    async def disconnect(self, reason: DisconnectReason) -> None:
        """
        On completion of this method, the peer will be disconnected
        and not in the peer pool anymore.
        """
        self.disconnect_nowait(reason)

        await self.manager.stop()