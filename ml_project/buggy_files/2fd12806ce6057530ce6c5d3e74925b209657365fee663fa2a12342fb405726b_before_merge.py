    def get_etag(self, href, account):
        """get etag for href

        type href: str()
        return: etag
        rtype: str()
        """
        sql_s = 'SELECT etag FROM {0} WHERE href=(?);'.format(account + '_m')
        etag = self.sql_ex(sql_s, (href,))[0][0]
        return etag