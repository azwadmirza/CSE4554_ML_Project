def retry_connection(func):
    @wraps(func)
    async def retry_connection_(self, *args):
        try:
            return await func(self, *args)
        except (
            asyncpg.PostgresConnectionError,
            asyncpg.ConnectionDoesNotExistError,
            asyncpg.ConnectionFailureError,
            asyncpg.InterfaceError,
        ):
            # Here we assume that a connection error has happened
            # Re-create connection and re-try the function call once only.
            if getattr(self, "transaction", None):
                self._finalized = True
                raise TransactionManagementError("Connection gone away during transaction")
            await self._lock.acquire()
            logging.info("Attempting reconnect")
            try:
                await self._close()
                await self.create_connection(with_db=True)
                logging.info("Reconnected")
            except Exception as e:
                logging.info("Failed to reconnect: %s", str(e))
                raise
            finally:
                self._lock.release()

            return await func(self, *args)

    return retry_connection_