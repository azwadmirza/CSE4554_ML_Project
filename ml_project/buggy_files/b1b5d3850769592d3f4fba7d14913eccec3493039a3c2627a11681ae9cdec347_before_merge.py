    async def _execute(self, query, args, limit, timeout, return_status=False):
        executor = lambda stmt, timeout: self._protocol.bind_execute(
            stmt, args, '', limit, return_status, timeout)
        timeout = self._protocol._get_timeout(timeout)
        with self._stmt_exclusive_section:
            return await self._do_execute(query, executor, timeout)