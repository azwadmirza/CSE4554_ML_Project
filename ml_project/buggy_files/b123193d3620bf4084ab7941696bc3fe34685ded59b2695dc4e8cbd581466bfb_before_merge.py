    def get_allday_range(self, start, end=None, account=None,
                         color='', readonly=False, unicode_symbols=True, show_deleted=True):
        if account is None:
            raise Exception('need to specify an account')
        strstart = start.strftime('%Y%m%d')
        if end is None:
            end = start + datetime.timedelta(days=1)
        strend = end.strftime('%Y%m%d')
        sql_s = ('SELECT href, dtstart, dtend FROM {0} WHERE '
                 'dtstart >= ? AND dtstart < ? OR '
                 'dtend > ? AND dtend <= ? OR '
                 'dtstart <= ? AND dtend > ? ').format(account + '_d')
        stuple = (strstart, strend, strstart, strend, strstart, strend)
        result = self.sql_ex(sql_s, stuple)
        event_list = list()
        for href, start, end in result:
            start = time.strptime(str(start), '%Y%m%d')
            end = time.strptime(str(end), '%Y%m%d')
            start = datetime.date(start.tm_year, start.tm_mon, start.tm_mday)
            end = datetime.date(end.tm_year, end.tm_mon, end.tm_mday)
            vevent = self.get_vevent_from_db(href, account,
                                             start=start, end=end,
                                             color=color,
                                             readonly=readonly,
                                             unicode_symbols=unicode_symbols)
            if show_deleted or vevent.status not in [DELETED, CALCHANGED, NEWDELETE]:
                event_list.append(vevent)
        return event_list