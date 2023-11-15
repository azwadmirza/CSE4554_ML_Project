    def resume_download(self, filename, setupDelay=0):

        try:
            config = self.load_download_config(filename)
            if not config:
                return
        except Exception as e:
            self._logger.exception("tlm: could not open checkpoint file %s", str(filename))
            return

        metainfo = config.get_metainfo()
        if not metainfo:
            self._logger.error("tlm: could not resume checkpoint %s; metainfo not found", filename)
            return
        if not isinstance(metainfo, dict):
            self._logger.error("tlm: could not resume checkpoint %s; metainfo is not dict %s %s",
                               filename, type(metainfo), repr(metainfo))
            return

        try:
            url = metainfo.get(b'url', None)
            url = url.decode('utf-8') if url else url
            tdef = (TorrentDefNoMetainfo(metainfo[b'infohash'], metainfo[b'name'], url)
                    if b'infohash' in metainfo else TorrentDef.load_from_dict(metainfo))
        except ValueError as e:
            self._logger.exception("tlm: could not restore tdef from metainfo dict: %s %s ", e, text_type(metainfo))
            return

        if config.get_bootstrap_download():
            if hexlify(tdef.get_infohash()) != self.session.config.get_bootstrap_infohash():
                self.remove_download_config(tdef.get_infohash())
                return

        config.state_dir = self.session.config.get_state_dir()

        self._logger.debug("tlm: load_checkpoint: resumedata %s", bool(config.get_engineresumedata()))
        if not (tdef and config):
            self._logger.info("tlm: could not resume checkpoint %s %s %s", filename, tdef, config)
            return

        if config.get_dest_dir() == '':  # removed torrent ignoring
            self._logger.info("tlm: removing checkpoint %s destdir is %s", filename, config.get_dest_dir())
            os.remove(filename)
            return

        try:
            if self.download_exists(tdef.get_infohash()):
                self._logger.info("tlm: not resuming checkpoint because download has already been added")
            elif config.get_credit_mining() and not self.session.config.get_credit_mining_enabled():
                self._logger.info("tlm: not resuming checkpoint since token mining is disabled")
            else:
                self.add(tdef, config, setupDelay=setupDelay)
        except Exception as e:
            self._logger.exception("tlm: load check_point: exception while adding download %s", tdef)