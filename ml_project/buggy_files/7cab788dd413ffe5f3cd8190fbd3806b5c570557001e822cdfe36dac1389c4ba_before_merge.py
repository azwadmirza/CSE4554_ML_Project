    async def commit(self):
        if self._finalized:
            raise TransactionManagementError("Transaction already finalised")
        self._finalized = True
        await self.transaction.commit()
        current_transaction_map[self.connection_name].set(self._old_context_value)