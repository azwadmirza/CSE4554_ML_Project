    def on_wallets(self, wallets):
        if not wallets:
            return
        self.wallets = wallets["wallets"]

        if 'MB' in self.wallets and self.wallets["MB"]["created"]:
            self.window().wallet_mc_overview_button.show()

        if 'BTC' in self.wallets and self.wallets["BTC"]["created"]:
            self.window().wallet_btc_overview_button.show()
        elif 'BTC' not in self.wallets:
            self.wallets['BTC'] = {
                'name': 'Bitcoin',
                'created': False,
                'identifier': 'BTC'
            }

        if 'TBTC' in self.wallets and self.wallets["TBTC"]["created"]:
            self.window().wallet_tbtc_overview_button.show()
        elif 'TBTC' not in self.wallets:
            self.wallets['TBTC'] = {
                'name': 'Testnet BTC',
                'created': False,
                'identifier': 'TBTC'
            }

        # Find out which wallets we still can create
        self.wallets_to_create = []
        for identifier, wallet in self.wallets.iteritems():
            if not wallet["created"]:
                self.wallets_to_create.append(identifier)

        if len(self.wallets_to_create) > 0:
            self.window().add_wallet_button.setEnabled(True)
        else:
            self.window().add_wallet_button.hide()