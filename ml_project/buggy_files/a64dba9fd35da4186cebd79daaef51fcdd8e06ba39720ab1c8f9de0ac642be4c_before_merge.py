    def get_state_record_for_inode(self, inode):
        cmd = "SELECT mtime, size, md5, timestamp from {} " "WHERE inode={}"
        cmd = cmd.format(self.STATE_TABLE, inode)
        self._execute(cmd)
        results = self._fetchall()
        if results:
            # uniquness constrain on inode
            assert len(results) == 1
            return results[0]
        return None