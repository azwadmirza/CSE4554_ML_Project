    def get_changed(self, account):
        """returns list of hrefs of locally edited vevents
        """
        self._check_account(account)
        sql_s = 'SELECT href FROM {0} WHERE status == (?)'.format(account + '_m')
        result = self.sql_ex(sql_s, (CHANGED, ))
        return [row[0] for row in result]