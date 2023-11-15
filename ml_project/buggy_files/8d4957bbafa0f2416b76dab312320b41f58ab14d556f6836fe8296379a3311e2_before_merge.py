    def sync_unspent(self):
        st = time.time()
        # block height needs to be real time for addition to our utxos:
        current_blockheight = self.bci.get_current_block_height()
        wallet_name = self.get_wallet_name()
        self.reset_utxos()

        listunspent_args = []
        if 'listunspent_args' in jm_single().config.options('POLICY'):
            listunspent_args = ast.literal_eval(jm_single().config.get(
                'POLICY', 'listunspent_args'))

        unspent_list = self.bci.rpc('listunspent', listunspent_args)
        # filter on label, but note (a) in certain circumstances (in-
        # wallet transfer) it is possible for the utxo to be labeled
        # with the external label, and (b) the wallet will know if it
        # belongs or not anyway (is_known_addr):
        our_unspent_list = [x for x in unspent_list if (
            self.bci.is_address_labeled(x, wallet_name) or
            self.bci.is_address_labeled(x, self.EXTERNAL_WALLET_LABEL))]
        for utxo in our_unspent_list:
            if not self.is_known_addr(utxo['address']):
                continue
            # The result of bitcoin core's listunspent RPC call does not have
            # a "height" field, only "confirmations".
            # But the result of scantxoutset used in no-history sync does
            # have "height".
            if "height" in utxo:
                height = utxo["height"]
            else:
                height = None
                # wallet's utxo database needs to store an absolute rather
                # than relative height measure:
                confs = int(utxo['confirmations'])
                if confs < 0:
                    jlog.warning("Utxo not added, has a conflict: " + str(utxo))
                    continue
                if confs >= 1:
                    height = current_blockheight - confs + 1
            self._add_unspent_txo(utxo, height)
        et = time.time()
        jlog.debug('bitcoind sync_unspent took ' + str((et - st)) + 'sec')