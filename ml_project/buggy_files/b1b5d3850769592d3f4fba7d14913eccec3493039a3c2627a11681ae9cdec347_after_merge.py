    async def _execute(self, query, args, limit, timeout, return_status=False):
        with self._stmt_exclusive_section:
            result, _ = await self.__execute(
                query, args, limit, timeout, return_status=return_status)
        return result