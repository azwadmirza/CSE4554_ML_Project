    def get_preimage_script(self, txin):
        # only for non-segwit
        if txin['type'] == 'p2pkh':
            return bitcoin.address_to_script(txin['address'])
        elif txin['type'] in ['p2sh', 'p2wsh', 'p2wsh-p2sh']:
            pubkeys, x_pubkeys = self.get_sorted_pubkeys(txin)
            return multisig_script(pubkeys, txin['num_sig'])
        elif txin['type'] in ['p2wpkh', 'p2wpkh-p2sh']:
            pubkey = txin['pubkeys'][0]
            pkh = bh2u(bitcoin.hash_160(bfh(pubkey)))
            return '76a9' + push_script(pkh) + '88ac'
        elif txin['type'] == 'p2pk':
            pubkey = txin['pubkeys'][0]
            return bitcoin.public_key_to_p2pk_script(pubkey)
        else:
            raise TypeError('Unknown txin type', txin['type'])