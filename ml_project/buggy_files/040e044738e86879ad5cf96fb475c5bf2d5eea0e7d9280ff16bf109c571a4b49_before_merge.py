    def query_balances(self) -> Dict[str, Dict]:
        self.query_ethereum_balances()
        self.query_btc_balances()
        return {'per_account': self.balances, 'totals': self.totals}