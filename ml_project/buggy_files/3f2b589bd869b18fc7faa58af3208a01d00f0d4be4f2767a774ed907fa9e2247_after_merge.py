    def get_master_year(self, master_id):
        """Fetches a master release given its Discogs ID and returns its year
        or None if the master release is not found.
        """
        self._log.debug(u'Searching for master release {0}', master_id)
        result = Master(self.discogs_client, {'id': master_id})

        self.request_start()
        try:
            year = result.fetch('year')
            self.request_finished()
            return year
        except DiscogsAPIError as e:
            if e.status_code != 404:
                self._log.debug(u'API Error: {0} (query: {1})', e,
                                result.data['resource_url'])
                if e.status_code == 401:
                    self.reset_auth()
                    return self.get_master_year(master_id)
            return None
        except CONNECTION_ERRORS:
            self._log.debug(u'Connection error in master release lookup',
                            exc_info=True)
            return None