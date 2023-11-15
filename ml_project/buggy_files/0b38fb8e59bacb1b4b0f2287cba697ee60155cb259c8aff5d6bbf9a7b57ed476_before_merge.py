    def _fetch_tx(self, txid):
        async def __fetch_parse(txid):
            return self.transaction_class(unhexlify(await self.network.get_transaction(txid)))
        return asyncio.ensure_future(__fetch_parse(txid))