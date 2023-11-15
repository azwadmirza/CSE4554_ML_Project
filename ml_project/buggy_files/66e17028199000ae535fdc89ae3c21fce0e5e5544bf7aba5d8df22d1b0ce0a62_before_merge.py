    async def _match_predictive_node_requests_to_peers(self) -> None:
        """
        Monitor for predictive nodes. These might be required by future blocks. They might not,
        because we run a speculative execution which might follow a different code path than
        the final block import does.

        When predictive nodes are queued up, ask the fastest available peasant (non-queen) peer
        for them. Without waiting for a response from the peer, continue and check if more
        predictive trie nodes are requested. Repeat indefinitely.
        """
        while self.manager.is_running:
            try:
                batch_id, hashes = await asyncio.wait_for(
                    self._maybe_useful_nodes.get(eth_constants.MAX_STATE_FETCH),
                    timeout=TOO_LONG_PREDICTIVE_PEER_DELAY,
                )
            except asyncio.TimeoutError:
                # Reduce the number of predictive peers, we seem to have plenty
                if self._min_predictive_peers > 0:
                    self._min_predictive_peers -= 1
                    self.logger.debug(
                        "Decremented predictive peers to %d",
                        self._min_predictive_peers,
                    )
                # Re-attempt
                continue

            try:
                peer = await asyncio.wait_for(
                    self._queen_tracker.pop_fastest_peasant(),
                    timeout=TOO_LONG_PREDICTIVE_PEER_DELAY,
                )
            except asyncio.TimeoutError:
                # Increase the minimum number of predictive peers, we seem to not have enough
                new_predictive_peers = min(
                    self._min_predictive_peers + 1,
                    # Don't reserve more than half the peers for prediction
                    self._num_peers // 2,
                )
                if new_predictive_peers != self._min_predictive_peers:
                    self.logger.debug(
                        "Updating predictive peer count from %d to %d",
                        self._min_predictive_peers,
                        new_predictive_peers,
                    )
                    self._min_predictive_peers = new_predictive_peers

                # Prepare to restart
                await self._maybe_useful_nodes.complete(batch_id, ())
                continue

            self._num_predictive_requests_by_peer[peer] += 1
            self._predictive_requests += 1

            self.manager.run_task(
                self._get_predictive_nodes_from_peer,
                peer,
                hashes,
                batch_id,
            )