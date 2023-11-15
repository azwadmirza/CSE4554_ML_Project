    def on_received_transactions(self, transactions):
        if not transactions:
            return
        for transaction in transactions["transactions"]:
            if self.wallets:
                asset1_prec = self.wallets[transaction["assets"]["first"]["type"]]["precision"]
                asset2_prec = self.wallets[transaction["assets"]["second"]["type"]]["precision"]
                item = TransactionWidgetItem(
                    self.window().market_transactions_list, transaction, asset1_prec, asset2_prec)
                self.window().market_transactions_list.addTopLevelItem(item)