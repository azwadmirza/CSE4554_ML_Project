    def mark_delete(self, href, account):
        """marks the entry as to be deleted on server on next sync
        """
        self._check_account(account)
        sql_s = 'UPDATE {0} SET STATUS = ? WHERE href = ?'.format(account + '_m')
        self.sql_ex(sql_s, (DELETED, href, ))