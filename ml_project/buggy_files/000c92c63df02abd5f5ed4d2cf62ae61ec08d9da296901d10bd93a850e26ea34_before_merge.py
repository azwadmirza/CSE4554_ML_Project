    def update(self, vevent, account, href='', etag='', status=OK):
        """insert a new or update an existing card in the db

        This is mostly a wrapper around two SQL statements, doing some cleanup
        before.

        :param vcard: vcard to be inserted or updated
        :type vcard: unicode
        :param href: href of the card on the server, if this href already
                     exists in the db the card gets updated. If no href is
                     given, a random href is chosen and it is implied that this
                     card does not yet exist on the server, but will be
                     uploaded there on next sync.
        :type href: str()
        :param etag: the etga of the vcard, if this etag does not match the
                     remote etag on next sync, this card will be updated from
                     the server. For locally created vcards this should not be
                     set
        :type etag: str()
        :param status: status of the vcard
                       * OK: card is in sync with remote server
                       * NEW: card is not yet on the server, this needs to be
                              set for locally created vcards
                       * CHANGED: card locally changed, will be updated on the
                                  server on next sync (if remote card has not
                                  changed since last sync)
                       * DELETED: card locally delete, will also be deleted on
                                  one the server on next sync (if remote card
                                  has not changed)
        :type status: one of backend.OK, backend.NEW, backend.CHANGED,
                      backend.DELETED


        """
        if not isinstance(vevent, icalendar.cal.Event):
            ical = icalendar.Event.from_ical(vevent)
            for component in ical.walk():
                if component.name == 'VEVENT':
                    vevent = component
        all_day_event = False
        if href == '' or href is None:
            href = get_random_href()
        if 'VALUE' in vevent['DTSTART'].params:
            if vevent['DTSTART'].params['VALUE'] == 'DATE':
                all_day_event = True

        dtstart = vevent['DTSTART'].dt

        if 'RRULE' in vevent.keys():
            rrulestr = vevent['RRULE'].to_ical()
            rrule = dateutil.rrule.rrulestr(rrulestr, dtstart=dtstart)
            today = datetime.datetime.today()
            if hasattr(dtstart, 'tzinfo') and dtstart.tzinfo is not None:
                # would be better to check if self is all day event
                today = self.conf.default.default_timezone.localize(today)
            rrule._until = today + datetime.timedelta(days=15 * 365)
            logging.debug('calculating recurrence dates for {0}, '
                          'this might take some time.'.format(href))
            dtstartl = list(rrule)
            if len(dtstartl) == 0:
                raise UpdateFailed('Unsupported recursion rule for event '
                                   '{0}:\n{1}'.format(href, vevent.to_ical()))

            if 'DURATION' in vevent.keys():
                duration = vevent['DURATION'].dt
            else:
                duration = vevent['DTEND'].dt - vevent['DTSTART'].dt
            dtstartend = [(start, start + duration) for start in dtstartl]
        else:
            if 'DTEND' in vevent.keys():
                dtend = vevent['DTEND'].dt
            else:
                dtend = vevent['DTSTART'].dt + vevent['DURATION'].dt
            dtstartend = [(dtstart, dtend)]

        for dbname in [account + '_d', account + '_dt']:
            sql_s = ('DELETE FROM {0} WHERE href == ?'.format(dbname))
            self.sql_ex(sql_s, (href, ), commit=False)

        for dtstart, dtend in dtstartend:
            if all_day_event:
                dbstart = dtstart.strftime('%Y%m%d')
                dbend = dtend.strftime('%Y%m%d')
                dbname = account + '_d'
            else:
                # TODO: extract strange (aka non Olson) TZs from params['TZID']
                # perhaps better done in model/vevent
                if dtstart.tzinfo is None:
                    dtstart = self.conf.default.default_timezone.localize(dtstart)
                if dtend.tzinfo is None:
                    dtend = self.conf.default.default_timezone.localize(dtend)

                dtstart_utc = dtstart.astimezone(pytz.UTC)
                dtend_utc = dtend.astimezone(pytz.UTC)
                dbstart = calendar.timegm(dtstart_utc.timetuple())
                dbend = calendar.timegm(dtend_utc.timetuple())
                dbname = account + '_dt'

            sql_s = ('INSERT INTO {0} '
                     '(dtstart, dtend, href) '
                     'VALUES (?, ?, ?);'.format(dbname))
            stuple = (dbstart,
                      dbend,
                      href)
            self.sql_ex(sql_s, stuple, commit=False)

        sql_s = ('INSERT OR REPLACE INTO {0} '
                 '(status, vevent, etag, href) '
                 'VALUES (?, ?, ?, '
                 'COALESCE((SELECT href FROM {0} WHERE href = ?), ?)'
                 ');'.format(account + '_m'))

        stuple = (status,
                  vevent.to_ical().decode('utf-8'),
                  etag,
                  href,
                  href)
        self.sql_ex(sql_s, stuple, commit=False)
        self.conn.commit()