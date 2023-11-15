    def remove_blockchain_account(self, blockchain, account):
        try:
            new_data = self.blockchain.remove_blockchain_account(blockchain, account)
        except InputError as e:
            return simple_result(False, str(e))
        self.data.remove_blockchain_account(blockchain, account)
        return accounts_result(new_data['per_account'], new_data['totals'])