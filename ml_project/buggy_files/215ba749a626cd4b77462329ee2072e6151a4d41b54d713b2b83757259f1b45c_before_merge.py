    def get_used(self, currency) -> float:

        balance = self._wallets.get(currency)
        if balance and balance.used:
            return balance.used
        else:
            return 0