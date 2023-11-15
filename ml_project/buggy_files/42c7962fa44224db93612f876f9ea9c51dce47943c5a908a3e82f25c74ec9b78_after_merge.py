    def update_button_texts(self):
        self.window().market_currency_type_button.setText("%s / %s" % (self.chosen_wallets[0], self.chosen_wallets[1]))
        self.window().create_ask_button.setText("Sell %s for %s" % (self.chosen_wallets[0], self.chosen_wallets[1]))
        self.window().create_bid_button.setText("Buy %s for %s" % (self.chosen_wallets[0], self.chosen_wallets[1]))

        # Update headers of the tree widget
        self.window().asks_list.headerItem().setText(1, '%s' % self.chosen_wallets[0])
        self.window().asks_list.headerItem().setText(2, 'Total (%s)' % self.chosen_wallets[0])
        self.window().bids_list.headerItem().setText(1, '%s' % self.chosen_wallets[0])
        self.window().bids_list.headerItem().setText(0, 'Total (%s)' % self.chosen_wallets[0])