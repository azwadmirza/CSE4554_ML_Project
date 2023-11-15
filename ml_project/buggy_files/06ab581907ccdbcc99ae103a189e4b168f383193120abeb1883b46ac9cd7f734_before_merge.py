    async def continuously_report(self) -> None:
        async for _ in trio_utils.every(self._reporting_frequency):
            self._reporter.report_now()