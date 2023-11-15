    def should_create_wallet(self, wallet_id):
        if wallet_id == "BTC" or wallet_id == "TBTC":
            # We check whether bitcoinlib is installed, if not, warn the user (should only happen on linux systems)
            try:
                import bitcoinlib
            except ImportError:
                ConfirmationDialog.show_error(self.window(), "bitcoinlib not found",
                                              "bitcoinlib could not be located on your system. "
                                              "Please install it using the following command: "
                                              "pip install bitcoinlib --user")
                return

        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("wallets/%s" % wallet_id, self.on_wallet_created, method='PUT', data='')