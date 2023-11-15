    def load_checkpoint(self, filename):
        try:
            config = DownloadConfig.load(filename)
        except Exception:
            self._logger.exception("Could not open checkpoint file %s", filename)
            return

        metainfo = config.get_metainfo()
        if not metainfo:
            self._logger.error("Could not resume checkpoint %s; metainfo not found", filename)
            return
        if not isinstance(metainfo, dict):
            self._logger.error("Could not resume checkpoint %s; metainfo is not dict %s %s",
                               filename, type(metainfo), repr(metainfo))
            return

        try:
            url = metainfo.get(b'url', None)
            url = url.decode('utf-8') if url else url
            tdef = (TorrentDefNoMetainfo(metainfo[b'infohash'], metainfo[b'name'], url)
                    if b'infohash' in metainfo else TorrentDef.load_from_dict(metainfo))
        except (KeyError, ValueError) as e:
            self._logger.exception("Could not restore tdef from metainfo dict: %s %s ", e, metainfo)
            return

        if config.get_bootstrap_download():
            if hexlify(tdef.get_infohash()) != self.tribler_session.config.get_bootstrap_infohash():
                self.remove_config(tdef.get_infohash())
                return

        config.state_dir = self.tribler_session.config.get_state_dir()
        if config.get_dest_dir() == '':  # removed torrent ignoring
            self._logger.info("Removing checkpoint %s destdir is %s", filename, config.get_dest_dir())
            os.remove(filename)
            return

        try:
            if self.download_exists(tdef.get_infohash()):
                self._logger.info("Not resuming checkpoint because download has already been added")
            elif config.get_credit_mining() and not self.tribler_session.config.get_credit_mining_enabled():
                self._logger.info("Not resuming checkpoint since token mining is disabled")
            else:
                self.start_download(tdef=tdef, config=config)
        except Exception:
            self._logger.exception("Not resume checkpoint due to exception while adding download")