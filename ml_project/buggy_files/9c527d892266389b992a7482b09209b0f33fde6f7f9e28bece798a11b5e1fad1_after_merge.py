    async def release(self, connection, *, timeout=None):
        """Release a database connection back to the pool.

        :param Connection connection:
            A :class:`~asyncpg.connection.Connection` object to release.
        :param float timeout:
            A timeout for releasing the connection.  If not specified, defaults
            to the timeout provided in the corresponding call to the
            :meth:`Pool.acquire() <asyncpg.pool.Pool.acquire>` method.

        .. versionchanged:: 0.14.0
            Added the *timeout* parameter.
        """
        async def _release_impl(ch: PoolConnectionHolder, timeout: float):
            try:
                await ch.release(timeout)
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

        if timeout is None:
            timeout = connection._holder._timeout

        # Use asyncio.shield() to guarantee that task cancellation
        # does not prevent the connection from being returned to the
        # pool properly.
        return await asyncio.shield(
            _release_impl(connection._holder, timeout), loop=self._loop)