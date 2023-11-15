    def get_address(self):
        if not self.created or not self.unlocked:
            return ''
        return str(self.wallet.get_receiving_address())