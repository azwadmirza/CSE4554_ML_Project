    def start_download(self, torrentfilename=None, infohash=None, tdef=None, dconfig=None):
        self._logger.debug(u"starting download: filename: %s, torrent def: %s", torrentfilename, tdef)

        if infohash is not None:
            assert isinstance(infohash, str), "infohash type: %s" % type(infohash)
            assert len(infohash) == 20, "infohash length is not 20: %s, %s" % (len(infohash), infohash)

        # the priority of the parameters is: (1) tdef, (2) infohash, (3) torrent_file.
        # so if we have tdef, infohash and torrent_file will be ignored, and so on.
        if tdef is None:
            if infohash is not None:
                # try to get the torrent from torrent_store if the infohash is provided
                torrent_data = self.tribler_session.get_collected_torrent(infohash)
                if torrent_data is not None:
                    # use this torrent data for downloading
                    tdef = TorrentDef.load_from_memory(torrent_data)

            if tdef is None:
                assert torrentfilename is not None, "torrent file must be provided if tdef and infohash are not given"
                # try to get the torrent from the given torrent file
                torrent_data = fix_torrent(torrentfilename)
                if torrent_data is None:
                    raise TorrentFileException("error while decoding torrent file")

                tdef = TorrentDef.load_from_memory(torrent_data)

        assert tdef is not None, "tdef MUST not be None after loading torrent"

        d = self.tribler_session.get_download(tdef.get_infohash())
        if d:
            # If there is an existing credit mining download with the same infohash, remove it and restart
            if d.get_credit_mining():
                self.tribler_session.lm.credit_mining_manager.torrents.pop(hexlify(tdef.get_infohash()), None)
                self.tribler_session.remove_download(d).addCallback(
                    lambda _, tf=torrentfilename, ih=infohash, td=tdef, dc=dconfig: self.start_download(tf, ih, td, dc)
                )
                return

            new_trackers = list(set(tdef.get_trackers_as_single_tuple()) - set(
                d.get_def().get_trackers_as_single_tuple()))
            if new_trackers:
                self.tribler_session.update_trackers(tdef.get_infohash(), new_trackers)

        default_dl_config = DefaultDownloadStartupConfig.getInstance()
        dscfg = default_dl_config.copy()

        if dconfig is not None:
            dscfg = dconfig

        self._logger.info('start_download: Starting in VOD mode')
        result = self.tribler_session.start_download_from_tdef(tdef, dscfg)

        return result