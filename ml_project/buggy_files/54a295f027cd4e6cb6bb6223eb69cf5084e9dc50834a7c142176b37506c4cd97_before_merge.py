    def get_new(self, account):
        """returns list of hrefs of locally added vcards
        """
        sql_s = 'SELECT href FROM {0} WHERE status == (?)'.format(account + '_m')
        result = self.sql_ex(sql_s, (NEW, ))
        return [row[0] for row in result]