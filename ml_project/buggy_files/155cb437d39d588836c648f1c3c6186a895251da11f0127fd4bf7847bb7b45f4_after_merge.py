    def add_torrent(self, torrentdl, atp):
        # If we are collecting the torrent for this infohash, abort this first.
        with self.metainfo_lock:
            ltsession = self.get_session(atp.pop('hops', 0))

            if 'ti' in atp:
                infohash = str(atp['ti'].info_hash())
            elif 'url' in atp:
                infohash = binascii.hexlify(parse_magnetlink(atp['url'])[1])
            else:
                raise ValueError('No ti or url key in add_torrent_params')

            # Check if we added this torrent before
            known = {str(h.info_hash()): h for h in ltsession.get_torrents()}
            existing_handle = known.get(infohash)
            if existing_handle:
                self.torrents[infohash] = (torrentdl, ltsession)
                return succeed(existing_handle)

            if infohash in self.torrents:
                self._logger.info("Torrent already exists in the downloads. Infohash:%s", infohash.encode('hex'))

            # Otherwise, add it anew
            ltsession.async_add_torrent(encode_atp(atp))
            self.torrents[infohash] = (torrentdl, ltsession)
            self._logger.debug("Adding torrent %s", infohash)
            return torrentdl.deferred_added