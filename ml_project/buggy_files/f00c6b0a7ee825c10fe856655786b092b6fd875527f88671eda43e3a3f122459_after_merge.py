    def _add_from_tx(self, tx: TransactionReceiptType) -> None:
        tx._confirmed.wait()
        if tx.status:
            try:
                self.at(tx.contract_address, tx.sender, tx)
            except ContractNotFound:
                # if the contract self-destructed during deployment
                pass