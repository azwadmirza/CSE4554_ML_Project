    async def continuously_report(self) -> None:
        while self.manager.is_running:
            super().report_now()
            await asyncio.sleep(self._reporting_frequency)