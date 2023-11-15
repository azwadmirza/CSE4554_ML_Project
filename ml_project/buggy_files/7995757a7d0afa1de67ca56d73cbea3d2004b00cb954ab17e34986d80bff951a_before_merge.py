    def selectWallet(self, testnet_seed=None):
        if jm_single().config.get("BLOCKCHAIN", "blockchain_source") != "regtest":
            # guaranteed to exist as load_program_config was called on startup:
            wallets_path = os.path.join(jm_single().datadir, 'wallets')
            firstarg = QFileDialog.getOpenFileName(self,
                                                   'Choose Wallet File',
                                                   wallets_path,
                                                   options=QFileDialog.DontUseNativeDialog)
            #TODO validate the file looks vaguely like a wallet file
            log.debug('Looking for wallet in: ' + str(firstarg))
            if not firstarg or not firstarg[0]:
                return
            decrypted = False
            while not decrypted:
                text, ok = QInputDialog.getText(self,
                                                'Decrypt wallet',
                                                'Enter your password:',
                                                echo=QLineEdit.Password)
                if not ok:
                    return
                pwd = str(text).strip()
                try:
                    decrypted = self.loadWalletFromBlockchain(firstarg[0], pwd)
                except Exception as e:
                    JMQtMessageBox(self,
                               str(e),
                               mbtype='warn',
                               title="Error")
                    return
        else:
            if not testnet_seed:
                testnet_seed, ok = QInputDialog.getText(self,
                                                        'Load Testnet wallet',
                                                        'Enter a testnet seed:',
                                                        QLineEdit.Normal)
                if not ok:
                    return
            firstarg = str(testnet_seed)
            pwd = None
            #ignore return value as there is no decryption failure possible
            self.loadWalletFromBlockchain(firstarg, pwd)