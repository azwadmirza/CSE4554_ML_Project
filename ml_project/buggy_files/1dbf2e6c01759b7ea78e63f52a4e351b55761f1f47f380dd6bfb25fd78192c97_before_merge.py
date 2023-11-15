    def href_exists(self, href, account):
        """returns True if href already exists in db

        :param href: href
        :type href: str()
        :returns: True or False
        """
        sql_s = 'SELECT href FROM {0} WHERE href = ?;'.format(account)
        if len(self.sql_ex(sql_s, (href, ))) == 0:
            return False
        else:
            return True