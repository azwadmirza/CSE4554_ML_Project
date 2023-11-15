    def _in_transaction(self):
        return self._transaction_class(self)