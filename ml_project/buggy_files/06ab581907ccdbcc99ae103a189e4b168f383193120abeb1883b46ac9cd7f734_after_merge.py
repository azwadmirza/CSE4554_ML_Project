    async def continuously_report(self) -> None:
        async for _ in trio_utils.every(self._reporting_frequency):
            super().report_now()