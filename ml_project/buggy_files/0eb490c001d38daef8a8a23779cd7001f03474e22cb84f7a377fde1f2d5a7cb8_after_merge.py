    async def _executemany(self, query, args, timeout):
        executor = lambda stmt, timeout: self._protocol.bind_execute_many(
            stmt, args, '', timeout)
        timeout = self._protocol._get_timeout(timeout)
        with self._stmt_exclusive_section:
            result, _ = await self._do_execute(query, executor, timeout)
        return result