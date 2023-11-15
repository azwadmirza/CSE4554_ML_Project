    def set_status(self, href, status, account):
        """sets the status of vcard
        """
        sql_s = 'UPDATE {0} SET STATUS = ? WHERE href = ?'.format(account + '_m')
        self.sql_ex(sql_s, (status, href, ))