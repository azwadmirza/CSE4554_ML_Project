    def delete(self, href, account):
        """
        removes the event from the db,
        returns nothing
        """
        logging.debug("locally deleting " + str(href))
        for dbname in [account + '_d', account + '_dt', account + '_m']:
            sql_s = 'DELETE FROM {0} WHERE href = ? ;'.format(dbname)
            self.sql_ex(sql_s, (href, ))