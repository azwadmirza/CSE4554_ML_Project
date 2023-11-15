        async def _release_impl(ch: PoolConnectionHolder, timeout: float):
            try:
                await ch.release(timeout)
            finally:
                self._queue.put_nowait(ch)