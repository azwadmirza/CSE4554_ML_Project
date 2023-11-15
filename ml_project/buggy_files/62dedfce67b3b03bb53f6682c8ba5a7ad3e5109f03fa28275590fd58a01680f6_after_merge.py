    def get_balance(self):
        """
        Return the balance of the wallet.
        """
        if self.created and self.unlocked:
            options = {'nolnet': False, 'password': None, 'verbose': False, 'cmd': 'getbalance',
                       'wallet_path': self.wallet_file, 'testnet': self.TESTNET, 'segwit': False,
                       'cwd': self.wallet_dir,
                       'portable': False}
            config = SimpleConfig(options)

            server = self.get_daemon().get_server(config)
            result = server.run_cmdline(options)

            confirmed = float(result['confirmed'])
            unconfirmed = float(result['unconfirmed']) if 'unconfirmed' in result else 0
            unconfirmed += (float(result['unmatured']) if 'unmatured' in result else 0)

            return succeed({
                "available": confirmed,
                "pending": unconfirmed,
                "currency": 'BTC'
            })

        return succeed({"available": 0, "pending": 0, "currency": 'BTC'})