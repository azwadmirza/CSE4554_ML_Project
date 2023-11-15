    def _lock_scan(self, scanid, oldlockid, newlockid):
        if oldlockid is not None:
            oldlockid = bson.Binary(oldlockid)
        if newlockid is not None:
            newlockid = bson.Binary(newlockid)
        scan = self.db[self.colname_scans].find_and_modify({
            "_id": scanid,
            "lock": oldlockid,
        }, {
            "$set": {"lock": newlockid},
        }, full_response=True, fields={'target': False}, new=True)['value']
        if "target_info" not in scan:
            target = self.get_scan_target(scanid)
            if target is not None:
                target_info = target.target.infos
                self.db[self.colname_scans].update(
                    {"_id": scanid},
                    {"$set": {"target_info": target_info}},
                )
                scan["target_info"] = target_info
        if scan is not None and scan['lock'] is not None:
            scan['lock'] = bytes(scan['lock'])
        return scan