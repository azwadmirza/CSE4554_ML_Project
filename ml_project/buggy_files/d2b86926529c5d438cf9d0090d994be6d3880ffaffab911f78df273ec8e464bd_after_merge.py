    async def read(
        self, n: int, timeout: TimeoutConfig = None, flag: TimeoutFlag = None
    ) -> bytes:
        if timeout is None:
            timeout = self.timeout

        while True:
            # Check our flag at the first possible moment, and use a fine
            # grained retry loop if we're not yet in read-timeout mode.
            should_raise = flag is None or flag.raise_on_read_timeout
            read_timeout = _or_inf(timeout.read_timeout if should_raise else 0.01)

            with trio.move_on_after(read_timeout):
                async with self.read_lock:
                    return await self.stream.receive_some(max_bytes=n)

            if should_raise:
                raise ReadTimeout() from None