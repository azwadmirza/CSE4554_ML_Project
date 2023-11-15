    def get_all_href_from_db(self, accounts):
        """returns a list with all hrefs
        """
        result = list()
        for account in accounts:
            self._check_account(account)
            hrefs = self.sql_ex('SELECT href FROM {0}'.format(account + '_m'))
            result = result + [(href[0], account) for href in hrefs]
        return result