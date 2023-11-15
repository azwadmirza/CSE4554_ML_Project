    async def jsonrpc_wallet_send(
            self, amount, addresses, wallet_id=None,
            change_account_id=None, funding_account_ids=None, preview=False):
        """
        Send the same number of credits to multiple addresses using all accounts in wallet to
        fund the transaction and the default account to receive any change.

        Usage:
            wallet_send <amount> <addresses>... [--wallet_id=<wallet_id>] [--preview]
                        [--change_account_id=None] [--funding_account_ids=<funding_account_ids>...]

        Options:
            --wallet_id=<wallet_id>         : (str) restrict operation to specific wallet
            --change_account_id=<wallet_id> : (str) account where change will go
            --funding_account_ids=<funding_account_ids> : (str) accounts to fund the transaction
            --preview                  : (bool) do not broadcast the transaction

        Returns: {Transaction}
        """
        wallet = self.wallet_manager.get_wallet_or_default(wallet_id)
        assert not wallet.is_locked, "Cannot spend funds with locked wallet, unlock first."
        account = wallet.get_account_or_default(change_account_id)
        accounts = wallet.get_accounts_or_all(funding_account_ids)

        amount = self.get_dewies_or_error("amount", amount)

        if addresses and not isinstance(addresses, list):
            addresses = [addresses]

        outputs = []
        for address in addresses:
            self.valid_address_or_error(address)
            outputs.append(
                Output.pay_pubkey_hash(
                    amount, self.ledger.address_to_hash160(address)
                )
            )

        tx = await Transaction.create(
            [], outputs, accounts, account
        )

        if not preview:
            await self.ledger.broadcast(tx)
            self.component_manager.loop.create_task(self.analytics_manager.send_credits_sent())
        else:
            await self.ledger.release_tx(tx)

        return tx