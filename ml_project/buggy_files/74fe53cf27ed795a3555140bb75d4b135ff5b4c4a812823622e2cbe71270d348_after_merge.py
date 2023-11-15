    def modify_blockchain_account(
            self,
            blockchain: str,
            account: typing.BlockchainAddress,
            append_or_remove: str,
            add_or_sub: Callable[[FVal, FVal], FVal],
    ) -> BlockchainBalancesUpdate:

        if blockchain == S_BTC:
            if append_or_remove == 'remove' and account not in self.accounts[S_BTC]:
                raise InputError('Tried to remove a non existing BTC account')
            self.modify_btc_account(account, append_or_remove, add_or_sub)

        elif blockchain == S_ETH:
            if append_or_remove == 'remove' and account not in self.accounts[S_ETH]:
                raise InputError('Tried to remove a non existing ETH account')
            try:
                self.modify_eth_account(account, append_or_remove, add_or_sub)
            except BadFunctionCallOutput as e:
                logger.error(
                    'Assuming unsynced chain. Got web3 BadFunctionCallOutput '
                    'exception: {}'.format(str(e))
                )
                raise EthSyncError(
                    'Tried to use the ethereum chain of a local client to edit '
                    'an eth account but the chain is not synced.'
                )

        else:
            raise InputError(
                'Unsupported blockchain {} provided at remove_blockchain_account'.format(
                    blockchain)
            )

        return {'per_account': self.balances, 'totals': self.totals}