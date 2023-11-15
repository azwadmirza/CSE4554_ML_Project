    def loadWalletFromBlockchain(self, firstarg=None, pwd=None):
        if firstarg:
            wallet_path = get_wallet_path(str(firstarg), None)
            try:
                wallet = open_test_wallet_maybe(wallet_path, str(firstarg),
                        None, ask_for_password=False, password=pwd.encode('utf-8') if pwd else None,
                        gap_limit=jm_single().config.getint("GUI", "gaplimit"))
            except RetryableStorageError as e:
                JMQtMessageBox(self,
                               str(e),
                               mbtype='warn',
                               title="Error")
                return False
            # only used for GUI display on regtest:
            self.testwalletname = wallet.seed = str(firstarg)
        if isinstance(wallet, FidelityBondMixin):
            raise Exception("Fidelity bond wallets not supported by Qt")
        if 'listunspent_args' not in jm_single().config.options('POLICY'):
            jm_single().config.set('POLICY', 'listunspent_args', '[0]')
        assert wallet, "No wallet loaded"

        # shut down any existing wallet service
        # monitoring loops
        if self.wallet_service is not None:
            if self.wallet_service.isRunning():
                self.wallet_service.stopService()
        if self.walletRefresh is not None:
            self.walletRefresh.stop()

        self.wallet_service = WalletService(wallet)

        if jm_single().bc_interface is None:
            self.centralWidget().widget(0).updateWalletInfo(
                get_wallet_printout(self.wallet_service))
            return True

        # add information callbacks:
        self.wallet_service.add_restart_callback(self.restartWithMsg)
        self.wallet_service.autofreeze_warning_cb = self.autofreeze_warning_cb
        self.wallet_service.startService()
        self.syncmsg = ""
        self.walletRefresh = task.LoopingCall(self.updateWalletInfo)
        self.walletRefresh.start(5.0)

        self.statusBar().showMessage("Reading wallet from blockchain ...")
        return True