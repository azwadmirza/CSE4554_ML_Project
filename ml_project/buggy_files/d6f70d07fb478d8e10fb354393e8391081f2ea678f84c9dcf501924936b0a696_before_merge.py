    async def add_outbound_peer(self, peer: BasePeer) -> None:
        try:
            await self._start_peer(peer)
        except asyncio.TimeoutError as err:
            self.logger.debug('Timeout waiting for %s to start: %s', peer, err)
            return

        await self._add_peer_and_bootstrap(peer)