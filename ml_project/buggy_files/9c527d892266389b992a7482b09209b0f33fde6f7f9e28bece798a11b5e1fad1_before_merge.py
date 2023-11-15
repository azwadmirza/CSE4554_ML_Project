    async def release(self, connection):
        """Release a database connection back to the pool."""
        async def _release_impl(ch: PoolConnectionHolder):
            try:
                await ch.release()
            finally:
                self._queue.put_nowait(ch)

        self._check_init()

        if (type(connection) is not PoolConnectionProxy or
                connection._holder._pool is not self):
            raise exceptions.InterfaceError(
                'Pool.release() received invalid connection: '
                '{connection!r} is not a member of this pool'.format(
                    connection=connection))

        if connection._con is None:
            # Already released, do nothing.
            return

        connection._detach()

        # Use asyncio.shield() to guarantee that task cancellation
        # does not prevent the connection from being returned to the
        # pool properly.
        return await asyncio.shield(_release_impl(connection._holder),
                                    loop=self._loop)