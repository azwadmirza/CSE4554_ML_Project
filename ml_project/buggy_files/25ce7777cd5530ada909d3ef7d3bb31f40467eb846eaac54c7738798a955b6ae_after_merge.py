    def get_status(self, href, account):
        """
        gets the status of the event associated with href in `account`
        """
        self._check_account(account)
        sql_s = 'SELECT status FROM {0} WHERE href = (?)'.format(account + '_m')
        return self.sql_ex(sql_s, (href, ))[0][0]