    def _in_transaction(self) -> "TransactionWrapper":
        return self._transaction_class(self)