    async def jsonrpc_channel_abandon(
            self, claim_id=None, txid=None, nout=None, account_id=None, wallet_id=None,
            preview=False, blocking=True):
        """
        Abandon one of my channel claims.

        Usage:
            channel_abandon [<claim_id> | --claim_id=<claim_id>]
                            [<txid> | --txid=<txid>] [<nout> | --nout=<nout>]
                            [--account_id=<account_id>] [--wallet_id=<wallet_id>]
                            [--preview] [--blocking]

        Options:
            --claim_id=<claim_id>     : (str) claim_id of the claim to abandon
            --txid=<txid>             : (str) txid of the claim to abandon
            --nout=<nout>             : (int) nout of the claim to abandon
            --account_id=<account_id> : (str) id of the account to use
            --wallet_id=<wallet_id>   : (str) restrict operation to specific wallet
            --preview                 : (bool) do not broadcast the transaction
            --blocking                : (bool) wait until abandon is in mempool

        Returns: {Transaction}
        """
        wallet = self.wallet_manager.get_wallet_or_default(wallet_id)
        assert not wallet.is_locked, "Cannot spend funds with locked wallet, unlock first."
        if account_id:
            account = wallet.get_account_or_error(account_id)
            accounts = [account]
        else:
            account = wallet.default_account
            accounts = wallet.accounts

        if txid is not None and nout is not None:
            claims = await self.ledger.get_claims(
                wallet=wallet, accounts=accounts, **{'txo.txid': txid, 'txo.position': nout}
            )
        elif claim_id is not None:
            claims = await self.ledger.get_claims(
                wallet=wallet, accounts=accounts, claim_id=claim_id
            )
        else:
            raise Exception('Must specify claim_id, or txid and nout')

        if not claims:
            raise Exception('No claim found for the specified claim_id or txid:nout')

        tx = await Transaction.create(
            [Input.spend(txo) for txo in claims], [], [account], account
        )

        if not preview:
            await self.broadcast_or_release(tx, blocking)
            await self.analytics_manager.send_claim_action('abandon')
        else:
            await account.ledger.release_tx(tx)

        return tx