    async def add_outbound_peer(self, peer: BasePeer) -> None:
        try:
            await self._start_peer(peer)
        except asyncio.TimeoutError as err:
            self.logger.debug('Timeout waiting for %s to start: %s', peer, err)
            return

        # Check again to see if we have *become* full since the previous check.
        if self.is_full:
            self.logger.debug(
                "Successfully connected to %s but peer pool is full.  Disconnecting.",
                peer,
            )
            await peer.disconnect(DisconnectReason.TOO_MANY_PEERS)
            return
        elif not self.manager.is_running:
            self.logger.debug(
                "Successfully connected to %s but peer pool is closing.  Disconnecting.",
                peer,
            )
            await peer.disconnect(DisconnectReason.CLIENT_QUITTING)
            return

        await self._add_peer_and_bootstrap(peer)