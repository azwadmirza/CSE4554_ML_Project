    def unlock_scan(self, scan):
        """Release lock for scanid. Returns True on success, and raises a
LockError on failure.

        """
        if scan.get('lock') is None:
            raise LockError('Cannot release lock for %r: scan is not '
                            'locked' % scan['_id'])
        scan = self._lock_scan(scan['_id'], scan['lock'].bytes, None)
        return scan['lock'] is None