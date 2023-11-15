    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            if issubclass(exc_type, TransactionManagementError):
                self.release()
            else:
                await self.rollback()
        else:
            await self.commit()