    async def read(
        self, n: int, timeout: TimeoutConfig = None, flag: TimeoutFlag = None
    ) -> bytes:
        if timeout is None:
            timeout = self.timeout

        while True:
            # Check our flag at the first possible moment, and use a fine
            # grained retry loop if we're not yet in read-timeout mode.
            should_raise = flag is None or flag.raise_on_read_timeout
            read_timeout = timeout.read_timeout if should_raise else 0.01
            try:
                async with self.read_lock:
                    data = await asyncio.wait_for(
                        self.stream_reader.read(n), read_timeout
                    )
            except asyncio.TimeoutError:
                if should_raise:
                    raise ReadTimeout() from None
                # FIX(py3.6): yield control back to the event loop to give it a chance
                # to cancel `.read(n)` before we retry.
                # This prevents concurrent `.read()` calls, which asyncio
                # doesn't seem to allow on 3.6.
                # See: https://github.com/encode/httpx/issues/382
                await asyncio.sleep(0)
            else:
                break

        return data