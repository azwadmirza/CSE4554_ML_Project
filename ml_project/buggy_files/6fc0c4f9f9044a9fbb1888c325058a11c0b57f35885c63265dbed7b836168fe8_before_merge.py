    def _in_transaction(self) -> "TransactionWrapper":
        return self._transaction_class(self.connection_name, self._connection, self._lock)