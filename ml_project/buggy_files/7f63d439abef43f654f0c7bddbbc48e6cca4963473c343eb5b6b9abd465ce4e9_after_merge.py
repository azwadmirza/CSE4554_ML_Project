    def on_transactions(self, transactions):
        if not transactions:
            return
        for transaction in transactions["transactions"]:
            item = QTreeWidgetItem(self.window().wallet_transactions_list)
            item.setText(0, "Sent" if transaction["outgoing"] else "Received")
            item.setText(1, transaction["from"])
            item.setText(2, transaction["to"])
            item.setText(3, "%g %s" % (transaction["amount"], transaction["currency"]))
            item.setText(4, "%g %s" % (transaction["fee_amount"], transaction["currency"]))
            item.setText(5, transaction["id"])
            timestamp = timestamp_to_time(float(transaction["timestamp"])) if transaction["timestamp"] != "False" else "-"
            item.setText(6, timestamp)
            self.window().wallet_transactions_list.addTopLevelItem(item)