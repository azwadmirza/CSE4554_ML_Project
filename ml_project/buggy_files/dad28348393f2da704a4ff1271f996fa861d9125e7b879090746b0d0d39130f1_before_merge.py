    async def _run_backfill(self) -> None:
        await self._begin_backfill.wait()
        if self._next_trie_root_hash is None:
            raise RuntimeError("Cannot start backfill when a recent trie root hash is unknown")

        loop = asyncio.get_event_loop()
        while self.manager.is_running:
            # Collect node hashes that might be missing; enough for a single request.
            # Collect batch before asking for peer, because we don't want to hold the
            #   peer idle, for a long time.
            required_data = await loop.run_in_executor(None, self._batch_of_missing_hashes)

            if len(required_data) == 0:
                # Nothing available to request, for one of two reasons:
                if self._check_complete():
                    self.logger.info("Downloaded all accounts, storage and bytecode state")
                    return
                else:
                    # There are active requests to peers, and we don't have enough information to
                    #   ask for any more trie nodes (for example, near the beginning, when the top
                    #   of the trie isn't available).
                    self.logger.debug("Backfill is waiting for more hashes to arrive")
                    await asyncio.sleep(PAUSE_SECONDS_IF_STATE_BACKFILL_STARVED)
                    continue

            await asyncio.wait(
                (
                    self._external_peasant_usage.until_silence(),
                    self.manager.wait_finished(),
                ),
                return_when=asyncio.FIRST_COMPLETED,
            )
            if not self.manager.is_running:
                break

            peer = await self._queening_queue.pop_fastest_peasant()

            self.manager.run_task(self._make_request, peer, required_data)