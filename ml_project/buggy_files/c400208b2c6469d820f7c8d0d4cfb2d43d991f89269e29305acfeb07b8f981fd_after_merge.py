    def lock_scan(self, scanid):
        """Acquire lock for scanid. Returns the new scan object on success,
and raises a LockError on failure.

        """
        lockid = uuid.uuid1()
        scan = self._lock_scan(scanid, None, lockid.bytes)
        if scan['lock'] is not None:
            # This might be a bug in uuid module, Python 2 only
            ##  File "/opt/python/2.6.9/lib/python2.6/uuid.py", line 145, in __init__
            ##    int = long(('%02x'*16) % tuple(map(ord, bytes)), 16)
            # scan['lock'] = uuid.UUID(bytes=scan['lock'])
            scan['lock'] = uuid.UUID(hex=utils.encode_hex(scan['lock']).decode())
        if scan['lock'] == lockid:
            return scan