    async def jsonrpc_support_create(
            self, claim_id, amount, tip=False, account_id=None, wallet_id=None, funding_account_ids=None,
            preview=False, blocking=False):
        """
        Create a support or a tip for name claim.

        Usage:
            support_create (<claim_id> | --claim_id=<claim_id>) (<amount> | --amount=<amount>)
                           [--tip] [--account_id=<account_id>] [--wallet_id=<wallet_id>]
                           [--preview] [--blocking] [--funding_account_ids=<funding_account_ids>...]

        Options:
            --claim_id=<claim_id>     : (str) claim_id of the claim to support
            --amount=<amount>         : (decimal) amount of support
            --tip                     : (bool) send support to claim owner, default: false.
            --account_id=<account_id> : (str) account to use for holding the transaction
            --wallet_id=<wallet_id>   : (str) restrict operation to specific wallet
          --funding_account_ids=<funding_account_ids>: (list) ids of accounts to fund this transaction
            --preview                 : (bool) do not broadcast the transaction
            --blocking                : (bool) wait until transaction is in mempool

        Returns: {Transaction}
        """
        wallet = self.wallet_manager.get_wallet_or_default(wallet_id)
        assert not wallet.is_locked, "Cannot spend funds with locked wallet, unlock first."
        funding_accounts = wallet.get_accounts_or_all(funding_account_ids)
        amount = self.get_dewies_or_error("amount", amount)
        claim = await self.ledger.get_claim_by_claim_id(wallet.accounts, claim_id)
        claim_address = claim.get_address(self.ledger)
        if not tip:
            account = wallet.get_account_or_default(account_id)
            claim_address = await account.receiving.get_or_create_usable_address()

        tx = await Transaction.support(
            claim.claim_name, claim_id, amount, claim_address, funding_accounts, funding_accounts[0]
        )

        if not preview:
            await self.broadcast_or_release(tx, blocking)
            await self.storage.save_supports({claim_id: [{
                'txid': tx.id,
                'nout': tx.position,
                'address': claim_address,
                'claim_id': claim_id,
                'amount': dewies_to_lbc(amount)
            }]})
            self.component_manager.loop.create_task(self.analytics_manager.send_claim_action('new_support'))
        else:
            await self.ledger.release_tx(tx)

        return tx