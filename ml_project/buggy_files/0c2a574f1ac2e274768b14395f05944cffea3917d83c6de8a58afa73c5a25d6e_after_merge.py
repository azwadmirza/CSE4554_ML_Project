    def _sync_caldav(self):
        syncer = caldav.Syncer(self._resource,
                               user=self._username,
                               password=self._password,
                               verify=self._ssl_verify,
                               auth=self._auth)
        #self._dbtool.check_account_table(self.name)
        logging.debug('syncing events in the next 365 days')
        start = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        start_utc = self._local_timezone.localize(start).astimezone(pytz.UTC)
        end_utc = start_utc + datetime.timedelta(days=365)
        href_etag_list = syncer.get_hel(start=start_utc, end=end_utc)
        need_update = self._dbtool.needs_update(self.name, href_etag_list)
        logging.debug('{number} event(s) need(s) an '
                      'update'.format(number=len(need_update)))
        vhe_list = syncer.get_vevents(need_update)
        for vevent, href, etag in vhe_list:
            try:
                self._dbtool.update(vevent,
                                    self.name,
                                    href=href,
                                    etag=etag)
            except backend.UpdateFailed as error:
                logging.error(error)
        # syncing local new events
        hrefs = self._dbtool.get_new(self.name)

        logging.debug('{number} new events need to be '
                      'uploaded'.format(number=len(hrefs)))
        try:
            for href in hrefs:
                event = self._dbtool.get_vevent_from_db(href, self.name)
                (href_new, etag_new) = syncer.upload(event.vevent,
                                                     self._default_timezone)
                self._dbtool.update_href(href,
                                         href_new,
                                         self.name,
                                         status=OK)
        except caldav.NoWriteSupport:
            logging.info('failed to upload a new event, '
                         'you need to enable write support to use this feature'
                         ', see the documentation.')

        # syncing locally modified events
        hrefs = self._dbtool.get_changed(self.name)
        for href in hrefs:
            event = self._dbtool.get_vevent_from_db(href, self.name)
            etag = syncer.update(event.vevent, event.href, event.etag)

        # looking for events deleted on the server but still in the local db
        locale_hrefs = self._dbtool.hrefs_by_time_range(start_utc,
                                                        end_utc,
                                                        self.name)
        remote_hrefs = [href for href, _ in href_etag_list]
        may_be_deleted = list(set(locale_hrefs) - set(remote_hrefs))
        if may_be_deleted != list():
            for href in may_be_deleted:
                if syncer.test_deleted(href) and self._dbtool.get_status(href, self.name) != NEW:
                    logging.debug('removing remotely deleted event {0} from '
                                  'the local db'.format(href))
                    self._dbtool.delete(href, self.name)