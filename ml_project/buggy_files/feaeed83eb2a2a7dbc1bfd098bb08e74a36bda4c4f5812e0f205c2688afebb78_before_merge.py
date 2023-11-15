    async def jsonrpc_support_abandon(
            self, claim_id=None, txid=None, nout=None, keep=None,
            account_id=None, wallet_id=None, preview=False, blocking=False):
        """
        Abandon supports, including tips, of a specific claim, optionally
        keeping some amount as supports.

        Usage:
            support_abandon [--claim_id=<claim_id>] [(--txid=<txid> --nout=<nout>)] [--keep=<keep>]
                            [--account_id=<account_id>] [--wallet_id=<wallet_id>]
                            [--preview] [--blocking]

        Options:
            --claim_id=<claim_id>     : (str) claim_id of the support to abandon
            --txid=<txid>             : (str) txid of the claim to abandon
            --nout=<nout>             : (int) nout of the claim to abandon
            --keep=<keep>             : (decimal) amount of lbc to keep as support
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
            supports = await self.ledger.get_supports(
                wallet=wallet, accounts=accounts, **{'txo.txid': txid, 'txo.position': nout}
            )
        elif claim_id is not None:
            supports = await self.ledger.get_supports(
                wallet=wallet, accounts=accounts, claim_id=claim_id
            )
        else:
            raise Exception('Must specify claim_id, or txid and nout')

        if not supports:
            raise Exception('No supports found for the specified claim_id or txid:nout')

        if keep is not None:
            keep = self.get_dewies_or_error('keep', keep)
        else:
            keep = 0

        outputs = []
        if keep > 0:
            outputs = [
                Output.pay_support_pubkey_hash(
                    keep, supports[0].claim_name, supports[0].claim_id, supports[0].pubkey_hash
                )
            ]

        tx = await Transaction.create(
            [Input.spend(txo) for txo in supports], outputs, accounts, account
        )

        if not preview:
            await self.broadcast_or_release(tx, blocking)
            await self.analytics_manager.send_claim_action('abandon')
        else:
            await self.ledger.release_tx(tx)

        return tx