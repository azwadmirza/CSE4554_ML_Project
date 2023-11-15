    def show_new_order_dialog(self, is_ask):
        if not self.wallets[self.chosen_wallets[0]]['created']:
            ConfirmationDialog.show_error(self.window(), "Wallet not available",
                                          "%s wallet not available, please create it first." % self.chosen_wallets[0])
            return
        elif not self.wallets[self.chosen_wallets[1]]['created']:
            ConfirmationDialog.show_error(self.window(), "Wallet not available",
                                          "%s wallet not available, please create it first." % self.chosen_wallets[1])
            return

        self.dialog = NewMarketOrderDialog(self.window().stackedWidget, is_ask, self.chosen_wallets[0], self.chosen_wallets[1])
        self.dialog.button_clicked.connect(self.on_new_order_action)
        self.dialog.show()