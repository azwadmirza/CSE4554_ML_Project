    async def close(self) -> None:
        # NOTE: StreamWriter instances expose a '.wait_closed()' coroutine function,
        # but using it has caused compatibility issues with certain sites in
        # the past (see https://github.com/encode/httpx/issues/634), which is
        # why we don't call it here.
        # This is fine, though, because '.close()' schedules the actual closing of the
        # stream, meaning that at best it will happen during the next event loop
        # iteration, and at worst asyncio will take care of it on program exit.
        async with self.write_lock:
            self.stream_writer.close()