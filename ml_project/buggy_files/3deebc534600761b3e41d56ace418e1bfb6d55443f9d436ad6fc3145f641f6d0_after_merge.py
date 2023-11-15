    def reset_flag(self, href, account):
        """
        resets the status for a given href to 0 (=not edited locally)
        """
        self._check_account(account)
        sql_s = 'UPDATE {0} SET status = ? WHERE href = ?'.format(account + '_m')
        self.sql_ex(sql_s, (OK, href, ))