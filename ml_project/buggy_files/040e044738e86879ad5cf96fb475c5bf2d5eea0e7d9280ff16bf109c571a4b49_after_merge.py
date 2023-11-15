    def query_balances(self) -> Tuple[Dict[str, Dict], str]:
        try:
            self.query_ethereum_balances()
        except BadFunctionCallOutput as e:
            logger.error(
                'Assuming unsynced chain. Got web3 BadFunctionCallOutput '
                'exception: {}'.format(str(e))
            )
            msg = (
                'Tried to use the ethereum chain of a local client to query '
                'an eth account but the chain is not synced.'
            )
            return {}, msg

        self.query_btc_balances()
        return {'per_account': self.balances, 'totals': self.totals}, ''