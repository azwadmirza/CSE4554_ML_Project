        async def _release_impl(ch: PoolConnectionHolder):
            try:
                await ch.release()
            finally:
                self._queue.put_nowait(ch)