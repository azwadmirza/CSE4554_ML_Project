    async def _acquire(self, timeout):
        async def _acquire_impl():
            ch = await self._queue.get()  # type: PoolConnectionHolder
            try:
                proxy = await ch.acquire()  # type: PoolConnectionProxy
            except Exception:
                self._queue.put_nowait(ch)
                raise
            else:
                return proxy

        self._check_init()
        if timeout is None:
            return await _acquire_impl()
        else:
            return await asyncio.wait_for(
                _acquire_impl(), timeout=timeout, loop=self._loop)