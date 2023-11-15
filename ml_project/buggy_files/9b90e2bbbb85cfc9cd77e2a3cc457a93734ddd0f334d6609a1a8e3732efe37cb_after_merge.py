    async def _announce(self, batch_size: typing.Optional[int] = 10):
        if not batch_size:
            return
        if not self.node.joined.is_set():
            await self.node.joined.wait()
        blob_hashes = await self.storage.get_blobs_to_announce()
        if blob_hashes:
            self.announce_queue.extend(blob_hashes)
            log.info("%i blobs to announce", len(blob_hashes))
        batch = []
        while len(self.announce_queue):
            cnt = 0
            announced = []
            while self.announce_queue and cnt < batch_size:
                blob_hash = self.announce_queue.pop()
                announced.append(blob_hash)
                batch.append(self.node.announce_blob(blob_hash))
                cnt += 1
            to_await = []
            while batch:
                to_await.append(batch.pop())
            if to_await:
                await asyncio.gather(*tuple(to_await), loop=self.loop)
                await self.storage.update_last_announced_blobs(announced, self.loop.time())
                log.info("announced %i blobs", len(announced))
        if self.running:
            self.pending_call = self.loop.call_later(60, self.announce, batch_size)