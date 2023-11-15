    def get_total(self, currency) -> float:

        balance = self._wallets.get(currency)
        if balance and balance.total:
            return balance.total
        else:
            return 0