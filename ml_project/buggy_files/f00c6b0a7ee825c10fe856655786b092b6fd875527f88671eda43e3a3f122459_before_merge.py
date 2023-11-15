    def _add_from_tx(self, tx: TransactionReceiptType) -> None:
        tx._confirmed.wait()
        if tx.status:
            self.at(tx.contract_address, tx.sender, tx)