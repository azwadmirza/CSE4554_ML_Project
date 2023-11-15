    async def close(self, *, timeout=None):
        """Close the connection gracefully.

        :param float timeout:
            Optional timeout value in seconds.

        .. versionchanged:: 0.14.0
           Added the *timeout* parameter.
        """
        if self.is_closed():
            return
        self._mark_stmts_as_closed()
        self._listeners.clear()
        self._log_listeners.clear()
        self._aborted = True
        try:
            await self._protocol.close(timeout)
        except Exception:
            # If we fail to close gracefully, abort the connection.
            self._aborted = True
            self._protocol.abort()
            raise
        finally:
            self._clean_tasks()