    async def add_keys(self, account, chain, keys):
        await self.db.executemany(
            "insert into pubkey_address (address, account, chain, position, pubkey) values (?, ?, ?, ?, ?)",
            ((pubkey.address, account.public_key.address, chain,
              position, sqlite3.Binary(pubkey.pubkey_bytes))
             for position, pubkey in keys)
        )