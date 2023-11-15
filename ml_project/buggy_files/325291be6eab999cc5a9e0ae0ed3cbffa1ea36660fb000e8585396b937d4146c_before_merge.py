    async def get_metainfo(self, infohash, timeout=30, hops=None, url=None):
        """
        Lookup metainfo for a given infohash. The mechanism works by joining the swarm for the infohash connecting
        to a few peers, and downloading the metadata for the torrent.
        :param infohash: The (binary) infohash to lookup metainfo for.
        :param timeout: A timeout in seconds.
        :param hops: the number of tunnel hops to use for this lookup. If None, use config default.
        :param url: Optional URL. Can contain trackers info, etc.
        :return: The metainfo
        """
        infohash_hex = hexlify(infohash)
        if infohash in self.metainfo_cache:
            self._logger.info('Returning metainfo from cache for %s', infohash_hex)
            return self.metainfo_cache[infohash]['meta_info']

        self._logger.info('Trying to fetch metainfo for %s', infohash_hex)
        if infohash in self.metainfo_requests:
            download = self.metainfo_requests[infohash][0]
            self.metainfo_requests[infohash][1] += 1
        elif infohash in self.downloads:
            download = self.downloads[infohash]
        else:
            tdef = TorrentDefNoMetainfo(infohash, 'metainfo request', url=url)
            dcfg = DownloadConfig()
            dcfg.set_hops(self.tribler_session.config.get_default_number_hops() if hops is None else hops)
            dcfg.set_upload_mode(True)  # Upload mode should prevent libtorrent from creating files
            dcfg.set_dest_dir(self.metadata_tmpdir)
            try:
                download = self.start_download(tdef=tdef, config=dcfg, hidden=True, checkpoint_disabled=True)
            except TypeError:
                return
            self.metainfo_requests[infohash] = [download, 1]

        try:
            metainfo = download.tdef.get_metainfo() or await wait_for(shield(download.future_metainfo), timeout)
            self._logger.info('Successfully retrieved metainfo for %s', infohash_hex)
            self.metainfo_cache[infohash] = {'time': timemod.time(), 'meta_info': metainfo}
        except (CancelledError, TimeoutError):
            metainfo = None
            self._logger.info('Failed to retrieve metainfo for %s', infohash_hex)

        if infohash in self.metainfo_requests:
            self.metainfo_requests[infohash][1] -= 1
            if self.metainfo_requests[infohash][1] <= 0:
                await self.remove_download(download, remove_content=True)
                self.metainfo_requests.pop(infohash)

        return metainfo