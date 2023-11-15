    def add_owned_eth_tokens(self, tokens):
        try:
            new_data = self.blockchain.track_new_tokens(tokens)
        except (InputError, EthSyncError) as e:
            return simple_result(False, str(e))

        self.data.write_owned_eth_tokens(self.blockchain.owned_eth_tokens)
        return accounts_result(new_data['per_account'], new_data['totals'])