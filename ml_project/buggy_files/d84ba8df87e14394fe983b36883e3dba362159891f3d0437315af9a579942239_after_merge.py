    def check_metainfo(self, infohash_hex):
        """
        Check whether we have received metainfo for a given infohash.
        :param infohash_hex: The infohash of the download to lookup, in hex format (because libtorrent gives us these
                             infohashes in hex)
        """
        infohash = unhexlify(infohash_hex)
        if infohash not in self.metainfo_requests:
            return

        handle, metainfo_deferreds = self.metainfo_requests.pop(infohash)
        if not handle.is_valid() or not handle.has_metadata():
            self._logger.warning("Handle (valid:%s, metadata:%s) - returning None as metainfo lookup result",
                                 handle.is_valid(), handle.has_metadata())
            for metainfo_deferred in metainfo_deferreds:
                metainfo_deferred.callback(None)
            return

        # There seems to be metainfo
        metainfo = {b"info": bdecode_compat(get_info_from_handle(handle).metadata())}
        trackers = [tracker.url for tracker in get_info_from_handle(handle).trackers()]
        peers = []
        leechers = 0
        seeders = 0
        for peer in handle.get_peer_info():
            peers.append(peer.ip)
            if peer.progress == 1:
                seeders += 1
            else:
                leechers += 1

        if trackers:
            if len(trackers) > 1:
                metainfo[b"announce-list"] = [trackers]
            metainfo[b"announce"] = trackers[0]
        else:
            metainfo[b"nodes"] = []

        metainfo[b"leechers"] = leechers
        metainfo[b"seeders"] = seeders

        self.metainfo_cache[infohash] = {'time': time.time(), 'meta_info': metainfo}
        for metainfo_deferred in metainfo_deferreds:
            metainfo_deferred.callback(metainfo)

        # Remove the torrent from the metainfo session
        self.ltsession_metainfo.remove_torrent(handle, 1)