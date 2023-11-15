    async def save_max_gap(self):
        gap = await self.get_max_gap()
        self.receiving.gap = max(20, gap['max_receiving_gap'] + 1)
        self.change.gap = max(6, gap['max_change_gap'] + 1)
        self.wallet.save()