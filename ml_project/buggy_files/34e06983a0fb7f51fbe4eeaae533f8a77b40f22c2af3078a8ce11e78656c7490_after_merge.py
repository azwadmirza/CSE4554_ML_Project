    def query_blockchain_balances(self):
        result, empty_or_error = self.rotkehlchen.blockchain.query_balances()
        return process_result({'result': result, 'message': empty_or_error})