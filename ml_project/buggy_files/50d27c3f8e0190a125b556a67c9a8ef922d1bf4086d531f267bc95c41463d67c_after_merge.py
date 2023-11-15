    def add_blockchain_account(self, blockchain, account):
        try:
            new_data = self.blockchain.add_blockchain_account(blockchain, account)
        except (InputError, EthSyncError) as e:
            return simple_result(False, str(e))
        self.data.add_blockchain_account(blockchain, account)
        return accounts_result(new_data['per_account'], new_data['totals'])