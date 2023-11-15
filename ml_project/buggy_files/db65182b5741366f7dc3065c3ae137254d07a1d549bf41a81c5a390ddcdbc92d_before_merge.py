    def unlock_scan(self, scan):
        if scan.get('lock') is None:
            raise ValueError('Scan is not locked')
        scan = self._lock_scan(scan['_id'], scan['lock'].bytes, None)
        return scan['lock'] is None