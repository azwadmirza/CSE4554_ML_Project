    def _convert_version_24(self):
        if not self._is_upgrade_method_needed(23, 23):
            return
        channels = self.get('channels', [])
        for c in channels:
            # convert revocation store to dict
            r = c['revocation_store']
            d = {}
            for i in range(49):
                v = r['buckets'][i]
                if v is not None:
                    d[str(i)] = v
            r['buckets'] = d
            c['revocation_store'] = r
        # convert channels to dict
        self.data['channels'] = { x['channel_id']: x for x in channels }
        # convert txi & txo
        txi = self.get('txi', {})
        for tx_hash, d in list(txi.items()):
            d2 = {}
            for addr, l in d.items():
                d2[addr] = {}
                for ser, v in l:
                    d2[addr][ser] = v
            txi[tx_hash] = d2
        self.data['txi'] = txi
        txo = self.get('txo', {})
        for tx_hash, d in list(txo.items()):
            d2 = {}
            for addr, l in d.items():
                d2[addr] = {}
                for n, v, cb in l:
                    d2[addr][str(n)] = (v, cb)
            txo[tx_hash] = d2
        self.data['txo'] = txo

        self.data['seed_version'] = 24