    def create_wallet(self, password=''):
        """
        Create a new bitcoin wallet.
        """
        self._logger.info("Creating wallet in %s", self.wallet_dir)

        if password is not None:
            try:
                self.set_wallet_password(password)
            except InitError:
                return fail(RuntimeError("Cannot initialize the keychain, unable to unlock the wallet!"))
        self.wallet_password = password

        def run_on_thread(thread_method):
            # We are running code that writes to the wallet on a separate thread.
            # This is done because Electrum does not allow writing to a wallet from a daemon thread.
            wallet_thread = Thread(target=thread_method, name="ethereum-create-wallet")
            wallet_thread.setDaemon(False)
            wallet_thread.start()
            wallet_thread.join()

        seed = Mnemonic('en').make_seed()
        k = keystore.from_seed(seed, '')
        k.update_password(None, password)
        self.storage.put('keystore', k.dump())
        self.storage.put('wallet_type', 'standard')
        self.storage.set_password(password, bool(password))
        run_on_thread(self.storage.write)

        self.wallet = ElectrumWallet(self.storage)
        self.wallet.synchronize()
        run_on_thread(self.wallet.storage.write)
        self.created = True
        self.unlocked = True

        self.start_daemon()
        self.open_wallet()

        self._logger.info("Bitcoin wallet saved in '%s'", self.wallet.storage.path)

        return succeed(None)