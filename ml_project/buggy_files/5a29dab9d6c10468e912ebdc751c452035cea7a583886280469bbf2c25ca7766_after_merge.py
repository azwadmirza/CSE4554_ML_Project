    async def start(self):
        await self._connection.begin()
        self._finalized = False
        current_transaction = current_transaction_map[self.connection_name]
        self._old_context_value = current_transaction.get()
        current_transaction.set(self)