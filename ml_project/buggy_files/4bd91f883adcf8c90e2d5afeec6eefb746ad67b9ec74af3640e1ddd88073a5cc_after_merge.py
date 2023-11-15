    def _sync_http(self):
        """
        simple syncer to import events from .ics files
        """
        import icalendar
        self.syncer = caldav.HTTPSyncer(self._resource,
                                        user=self._username,
                                        password=self._password,
                                        verify=self._ssl_verify,
                                        auth=self._auth)
        #self._dbtool.check_account_table(self.name)
        ics = self.syncer.get_ics()
        cal = icalendar.Calendar.from_ical(ics)
        remote_uids = list()
        for component in cal.walk():
            if component.name in ['VEVENT']:
                remote_uids.append(str(component['UID']))
                try:
                    self._dbtool.update(component,
                                        self.name,
                                        href=str(component['UID']),
                                        etag='',
                                        status=OK)
                except backend.UpdateFailed as error:
                    logging.error(error)
        # events from an icalendar retrieved over stupid http have no href
        # themselves, so their uid is safed in the `href` column
        locale_uids = [uid for uid, account in self._dbtool.get_all_href_from_db([self.name])]
        remote_deleted = list(set(locale_uids) - set(remote_uids))
        if remote_deleted != list():
            for uid in remote_deleted:
                logging.debug('removing remotely deleted event {0} from '
                              'the local db'.format(uid))
                self._dbtool.delete(uid, self.name)