    def __str__(self) -> str:
        return _("{user}'s balance cannot rise above {max:,} {currency}.").format(
            user=self.user, max=self.max_balance, currency=self.currency_name
        )