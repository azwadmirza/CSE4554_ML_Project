    def update_from_torrent_search_results(self, search_results):
        """
        Updates the torrent database with the provided search results. It also checks for conflicting torrents, meaning
        if torrent already exists in the database, we simply ignore the search result.
        """
        for result in search_results:
            (infohash, name, length, num_files, category_list, creation_date, seeders, leechers, cid) = result
            torrent_item = SearchResponseItemPayload(infohash, name, length, num_files, category_list,
                                                     creation_date, seeders, leechers, cid)
            if self.has_torrent(infohash):
                db_torrent = self.get_torrent(infohash)
                if db_torrent['name'] and db_torrent['name'] == torrent_item.name:
                    self.logger.info("Conflicting names for torrent. Ignoring the response")
                    continue
            else:
                self.logger.debug("Adding new torrent from search results to database")
                self.torrent_db.addOrGetTorrentID(infohash)

            # Update local database
            self.torrent_db.updateTorrent(infohash, notify=False, name=torrent_item.name,
                                          length=torrent_item.length,
                                          creation_date=torrent_item.creation_date,
                                          num_files=torrent_item.num_files,
                                          comment='')