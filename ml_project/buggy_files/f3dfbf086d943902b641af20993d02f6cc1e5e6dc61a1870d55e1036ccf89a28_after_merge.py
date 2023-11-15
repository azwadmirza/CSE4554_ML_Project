    def get_transactions(self):
        if not self.created or not self.unlocked:
            return succeed([])

        options = {'nolnet': False, 'password': None, 'verbose': False, 'cmd': 'history',
                   'wallet_path': self.wallet_file, 'testnet': self.TESTNET, 'segwit': False, 'cwd': self.wallet_dir,
                   'portable': False}
        config = SimpleConfig(options)

        server = self.get_daemon().get_server(config)
        try:
            result = server.run_cmdline(options)
        except ProtocolError:
            self._logger.error("Unable to fetch transactions from BTC wallet!")
            return succeed([])

        transactions = []
        for transaction in result:
            outgoing = transaction['value'] < 0
            from_address = ','.join(transaction['input_addresses'])
            to_address = ','.join(transaction['output_addresses'])

            transactions.append({
                'id': transaction['txid'],
                'outgoing': outgoing,
                'from': from_address,
                'to': to_address,
                'amount': abs(transaction['value']),
                'fee_amount': 0.0,
                'currency': 'BTC',
                'timestamp': str(transaction['timestamp']),
                'description': 'Confirmations: %d' % transaction['confirmations']
            })

        return succeed(transactions)