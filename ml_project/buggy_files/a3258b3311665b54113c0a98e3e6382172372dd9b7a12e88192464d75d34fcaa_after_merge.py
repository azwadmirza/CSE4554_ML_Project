    def get_marked_delete(self, account):
        """returns list of tuples (hrefs, etags) of locally deleted vcards
        """
        self._check_account(account)
        sql_s = ('SELECT href, etag FROM {0} WHERE status == '
                 '(?)'.format(account + '_m'))
        result = self.sql_ex(sql_s, (DELETED, ))
        return result