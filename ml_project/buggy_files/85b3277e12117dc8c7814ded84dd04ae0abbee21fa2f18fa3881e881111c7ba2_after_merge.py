    def on_wallet_created(self, response):
        if not response:
            return
        if self.dialog:
            self.dialog.close_dialog()
            self.dialog = None
        self.load_wallets()