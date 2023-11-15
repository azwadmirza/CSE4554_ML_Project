    async def wait_closed(self):
        """
        Wait for the long-polling to close

        :return:
        """
        await asyncio.shield(self._close_waiter)