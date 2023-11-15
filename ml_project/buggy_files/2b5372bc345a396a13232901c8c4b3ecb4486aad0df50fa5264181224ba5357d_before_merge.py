    def get_transactions(self):
        if not self.created:
            return succeed([])

        # Update all transactions
        self.wallet.transactions_update(network=self.network)

        txs = self.wallet._session.query(DbTransaction.raw, DbTransaction.confirmations,
                                         DbTransaction.date, DbTransaction.fee)\
            .filter(DbTransaction.wallet_id == self.wallet.wallet_id)\
            .all()
        transactions = []

        for db_result in txs:
            transaction = Transaction.import_raw(db_result[0], network=self.network)
            transaction.confirmations = db_result[1]
            transaction.date = db_result[2]
            transaction.fee = db_result[3]
            transactions.append(transaction)

        # Sort them based on locktime
        transactions.sort(key=lambda tx: tx.locktime, reverse=True)

        my_keys = [key.address for key in self.wallet.keys(network=self.network, is_active=False)]

        transactions_list = []
        for transaction in transactions:
            value = 0
            input_addresses = []
            output_addresses = []
            for tx_input in transaction.inputs:
                input_addresses.append(tx_input.address)
                if tx_input.address in my_keys:
                    # At this point, we do not have the value of the input so we should do a database query for it
                    db_res = self.wallet._session.query(DbTransactionInput.value).filter(
                        tx_input.prev_hash.encode('hex') == DbTransactionInput.prev_hash,
                        tx_input.output_n_int == DbTransactionInput.output_n).all()
                    if db_res:
                        value -= db_res[0][0]

            for tx_output in transaction.outputs:
                output_addresses.append(tx_output.address)
                if tx_output.address in my_keys:
                    value += tx_output.value

            transactions_list.append({
                'id': transaction.hash,
                'outgoing': value < 0,
                'from': ','.join(input_addresses),
                'to': ','.join(output_addresses),
                'amount': abs(value),
                'fee_amount': transaction.fee,
                'currency': 'BTC',
                'timestamp': time.mktime(transaction.date.timetuple()),
                'description': 'Confirmations: %d' % transaction.confirmations
            })

        return succeed(transactions_list)