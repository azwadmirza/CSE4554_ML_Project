    def hrefs_by_time_range_datetime(self, start, end, account, color=''):
        """returns
        :type start: datetime.datetime
        :type end: datetime.datetime
        """
        self._check_account(account)
        start = time.mktime(start.timetuple())
        end = time.mktime(end.timetuple())
        sql_s = ('SELECT href FROM {0} WHERE '
                 'dtstart >= ? AND dtstart <= ? OR '
                 'dtend >= ? AND dtend <= ? OR '
                 'dtstart <= ? AND dtend >= ?').format(account + '_dt')
        stuple = (start, end, start, end, start, end)
        result = self.sql_ex(sql_s, stuple)
        return [one[0] for one in result]