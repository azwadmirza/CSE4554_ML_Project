    def _lock_scan(self, scanid, oldlockid, newlockid):
        """Change lock for scanid from oldlockid to newlockid. Returns the new
scan object on success, and raises a LockError on failure.

        """
        if oldlockid is not None:
            oldlockid = bson.Binary(oldlockid)
        if newlockid is not None:
            newlockid = bson.Binary(newlockid)
        scan = self.db[self.colname_scans].find_and_modify({
            "_id": scanid,
            "lock": oldlockid,
        }, {
            "$set": {"lock": newlockid, "pid": os.getpid()},
        }, full_response=True, fields={'target': False}, new=True)['value']
        if scan is None:
            if oldlockid is None:
                raise LockError('Cannot acquire lock for %r' % scanid)
            if newlockid is None:
                raise LockError('Cannot release lock for %r' % scanid)
            raise LockError('Cannot change lock for %r from '
                            '%r to %r' % (scanid, oldlockid, newlockid))
        if "target_info" not in scan:
            target = self.get_scan_target(scanid)
            if target is not None:
                target_info = target.target.infos
                self.db[self.colname_scans].update(
                    {"_id": scanid},
                    {"$set": {"target_info": target_info}},
                )
                scan["target_info"] = target_info
        if scan['lock'] is not None:
            scan['lock'] = bytes(scan['lock'])
        return scan