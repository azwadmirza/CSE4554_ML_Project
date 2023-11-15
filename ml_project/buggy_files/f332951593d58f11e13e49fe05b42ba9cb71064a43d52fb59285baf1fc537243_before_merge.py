    def get_address(self):
        if not self.created:
            return ''
        return str(self.wallet.get_receiving_address())