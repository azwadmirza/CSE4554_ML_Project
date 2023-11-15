    def _process_scrape_response(self, body):
        """
        This function handles the response body of a HTTP tracker,
        parsing the results.
        """
        # parse the retrieved results
        if body is None:
            self.failed(msg="no response body")
            return

        response_dict = bdecode(body)
        if not response_dict:
            self.failed(msg="no valid response")
            return

        response_list = []

        unprocessed_infohash_list = self._infohash_list[:]
        if b'files' in response_dict and isinstance(response_dict[b'files'], dict):
            for infohash in response_dict[b'files']:
                complete = 0
                incomplete = 0
                if isinstance(response_dict[b'files'][infohash], dict):
                    complete = response_dict[b'files'][infohash].get(b'complete', 0)
                    incomplete = response_dict[b'files'][infohash].get(b'incomplete', 0)

                # Sow complete as seeders. "complete: number of peers with the entire file, i.e. seeders (integer)"
                #  - https://wiki.theory.org/BitTorrentSpecification#Tracker_.27scrape.27_Convention
                seeders = complete
                leechers = incomplete

                # Store the information in the dictionary
                response_list.append({'infohash': hexlify(infohash), 'seeders': seeders, 'leechers': leechers})

                # remove this infohash in the infohash list of this session
                if infohash in unprocessed_infohash_list:
                    unprocessed_infohash_list.remove(infohash)

        elif b'failure reason' in response_dict:
            self._logger.info(u"%s Failure as reported by tracker [%s]", self, repr(response_dict[b'failure reason']))
            self.failed(msg=repr(response_dict[b'failure reason']))
            return

        # handle the infohashes with no result (seeders/leechers = 0/0)
        for infohash in unprocessed_infohash_list:
            response_list.append({'infohash': hexlify(infohash), 'seeders': 0, 'leechers': 0})

        self._is_finished = True
        if self.result_deferred and not self.result_deferred.called:
            self.result_deferred.callback({self.tracker_url: response_list})