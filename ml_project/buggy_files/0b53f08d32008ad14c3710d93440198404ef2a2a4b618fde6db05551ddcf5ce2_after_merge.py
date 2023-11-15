    def get_time_range(self, start, end, account, color='', readonly=False,
                       unicode_symbols=True, show_deleted=True):
        """returns
        :type start: datetime.datetime
        :type end: datetime.datetime
        :param deleted: include deleted events in returned lsit
        """
        self._check_account(account)
        start = time.mktime(start.timetuple())
        end = time.mktime(end.timetuple())
        sql_s = ('SELECT href, dtstart, dtend FROM {0} WHERE '
                 'dtstart >= ? AND dtstart <= ? OR '
                 'dtend >= ? AND dtend <= ? OR '
                 'dtstart <= ? AND dtend >= ?').format(account + '_dt')
        stuple = (start, end, start, end, start, end)
        result = self.sql_ex(sql_s, stuple)
        event_list = list()
        for href, start, end in result:
            start = pytz.UTC.localize(datetime.datetime.utcfromtimestamp(start))
            end = pytz.UTC.localize(datetime.datetime.utcfromtimestamp(end))
            event = self.get_vevent_from_db(href, account,
                                            start=start, end=end,
                                            color=color,
                                            readonly=readonly,
                                            unicode_symbols=unicode_symbols)
            if show_deleted or event.status not in [DELETED, CALCHANGED, NEWDELETE]:
                event_list.append(event)

        return event_list