    def get_vevent_from_db(self, href, account, start=None, end=None,
                           readonly=False, color=lambda x: x,
                           unicode_symbols=True):
        """returns the Event matching href, if start and end are given, a
        specific Event from a Recursion set is returned, the Event as saved in
        the db

        All other parameters given to this function are handed over to the
        Event.
        """
        self._check_account(account)
        sql_s = 'SELECT vevent, status, etag FROM {0} WHERE href=(?)'.format(account + '_m')
        result = self.sql_ex(sql_s, (href, ))
        return Event(result[0][0],
                     local_tz=self.conf.default.local_timezone,
                     default_tz=self.conf.default.default_timezone,
                     start=start,
                     end=end,
                     color=color,
                     href=href,
                     account=account,
                     status=result[0][1],
                     readonly=readonly,
                     etag=result[0][2],
                     unicode_symbols=unicode_symbols)