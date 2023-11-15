    def show_new_order_dialog(self, is_ask):
        self.dialog = NewMarketOrderDialog(self.window().stackedWidget, is_ask, self.chosen_wallets[0], self.chosen_wallets[1])
        self.dialog.button_clicked.connect(self.on_new_order_action)
        self.dialog.show()