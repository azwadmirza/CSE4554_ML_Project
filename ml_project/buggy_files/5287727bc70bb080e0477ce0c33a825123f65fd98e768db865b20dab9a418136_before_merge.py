    def on_wallets(self, wallets):
        wallets = wallets["wallets"]

        currency_wallets = ['BTC']
        total_currency_wallets = 0
        for wallet_id in wallets.keys():
            if wallet_id in currency_wallets:
                total_currency_wallets += 1

        if currency_wallets == 0:
            self.window().market_create_wallet_button.show()
            self.window().create_ask_button.hide()
            self.window().create_bid_button.hide()

        self.wallets = []
        for wallet_id in wallets.keys():
            self.wallets.append(wallet_id)

        if self.chosen_wallets is None and len(self.wallets) >= 2:
            self.chosen_wallets = (self.wallets[0], self.wallets[1])
            self.update_button_texts()

        for wallet_id, wallet in wallets.iteritems():
            if not wallet['created']:
                continue

            if wallet_id not in self.wallet_widgets:
                wallet_widget = MarketCurrencyBox(self.window().market_header_widget, wallets[wallet_id]['name'])
                self.window().market_header_widget.layout().insertWidget(4, wallet_widget)
                wallet_widget.setFixedWidth(100)
                wallet_widget.setFixedHeight(34)
                wallet_widget.show()
                self.wallet_widgets[wallet_id] = wallet_widget

                spacer = QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.window().market_header_widget.layout().insertSpacerItem(5, spacer)

            # The total balance keys might be different between wallet
            balance_amount = wallet['balance']['available']
            balance_currency = None

            if wallet_id == 'PP' or wallet_id == 'ABNA' or wallet_id == 'RABO':
                balance_currency = wallet['balance']['currency']

            self.wallet_widgets[wallet_id].update_with_amount(balance_amount, balance_currency)

        self.load_asks()
        self.load_bids()