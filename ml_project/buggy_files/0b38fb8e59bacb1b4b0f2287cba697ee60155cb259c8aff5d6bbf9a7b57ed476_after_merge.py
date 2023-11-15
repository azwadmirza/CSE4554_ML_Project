    async def _fetch_tx(self, txid):
        return self.transaction_class(unhexlify(await self.network.get_transaction(txid)))