    def query_blockchain_balances(self):
        balances = self.rotkehlchen.blockchain.query_balances()
        return process_result(balances)