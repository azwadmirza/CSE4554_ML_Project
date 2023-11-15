    async def release(self, timeout):
        assert self._in_use
        self._in_use = False
        self._timeout = None

        self._con._on_release()

        if self._con.is_closed():
            self._con = None

        elif self._con._protocol.queries_count >= self._max_queries:
            try:
                await self._con.close(timeout=timeout)
            finally:
                self._con = None

        else:
            try:
                budget = timeout

                if self._con._protocol._is_cancelling():
                    # If the connection is in cancellation state,
                    # wait for the cancellation
                    started = time.monotonic()
                    await asyncio.wait_for(
                        self._con._protocol._wait_for_cancellation(),
                        budget, loop=self._pool._loop)
                    if budget is not None:
                        budget -= time.monotonic() - started

                await self._con.reset(timeout=budget)
            except Exception as ex:
                # If the `reset` call failed, terminate the connection.
                # A new one will be created when `acquire` is called
                # again.
                try:
                    # An exception in `reset` is most likely caused by
                    # an IO error, so terminate the connection.
                    self._con.terminate()
                finally:
                    self._con = None
                    raise ex

        assert self._inactive_callback is None
        if self._max_inactive_time and self._con is not None:
            self._inactive_callback = self._pool._loop.call_later(
                self._max_inactive_time, self._deactivate_connection)