    def create_wallet(self):
        """
        Create a new bitcoin wallet.
        """
        from bitcoinlib.wallets import HDWallet, WalletError

        self._logger.info("Creating wallet in %s", self.wallet_dir)
        try:
            self.wallet = HDWallet.create(self.wallet_name, network=self.network, databasefile=self.db_path)
            self.wallet.new_key('tribler_payments')
            self.wallet.new_key('tribler_change', change=1)
            self.created = True
        except WalletError as exc:
            self._logger.error("Cannot create BTC wallet!")
            return fail(Failure(exc))
        return succeed(None)