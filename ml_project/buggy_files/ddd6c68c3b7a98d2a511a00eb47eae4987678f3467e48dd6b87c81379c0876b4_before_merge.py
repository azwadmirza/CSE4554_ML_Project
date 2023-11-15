def retry_connection(func):
    @wraps(func)
    async def wrapped(self, *args):
        try:
            return await func(self, *args)
        except (
            asyncpg.PostgresConnectionError,
            asyncpg.ConnectionDoesNotExistError,
            asyncpg.ConnectionFailureError,
        ):
            # Here we assume that a connection error has happened
            # Re-create connection and re-try the function call once only.
            await self._lock.acquire()
            logging.info("Attempting reconnect")
            try:
                await self._close()
                await self.create_connection(with_db=True)
                logging.info("Reconnected")
            except Exception:
                logging.info("Failed to reconnect")
            finally:
                self._lock.release()

            return await func(self, *args)

    return wrapped