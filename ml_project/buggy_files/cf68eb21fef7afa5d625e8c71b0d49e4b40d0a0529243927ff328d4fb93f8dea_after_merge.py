    def resume_download(self, filename, setupDelay=0):

        try:
            pstate = self.load_download_pstate(filename)
            if not pstate:
                return
        except Exception as e:
            self._logger.exception("tlm: could not open checkpoint file %s", str(filename))
            return

        metainfo = pstate.get('state', 'metainfo')
        if not metainfo:
            self._logger.error("tlm: could not resume checkpoint %s; metainfo not found", filename)
            return

        tdef = (TorrentDefNoMetainfo(metainfo['infohash'], metainfo['name'], metainfo.get('url', None))
                if 'infohash' in metainfo else TorrentDef.load_from_dict(metainfo))

        if (pstate.has_option('download_defaults', 'saveas') and
                isinstance(pstate.get('download_defaults', 'saveas'), tuple)):
            pstate.set('download_defaults', 'saveas', pstate.get('download_defaults', 'saveas')[-1])

        # If save_path is relative, make it global instead

        dscfg = DownloadStartupConfig(pstate, state_dir=self.session.config.get_state_dir())

        self._logger.debug("tlm: load_checkpoint: resumedata %s",
                           'len %s ' % (len(pstate.get('state', 'engineresumedata'))
                                        if pstate.get('state', 'engineresumedata') else 'None'))
        if not (tdef and dscfg):
            self._logger.info("tlm: could not resume checkpoint %s %s %s", filename, tdef, dscfg)
            return

        if dscfg.get_dest_dir() == '':  # removed torrent ignoring
            self._logger.info("tlm: removing checkpoint %s destdir is %s", filename, dscfg.get_dest_dir())
            os.remove(filename)
            return

        try:
            if self.download_exists(tdef.get_infohash()):
                self._logger.info("tlm: not resuming checkpoint because download has already been added")
            elif dscfg.get_credit_mining() and not self.session.config.get_credit_mining_enabled():
                self._logger.info("tlm: not resuming checkpoint since token mining is disabled")
            else:
                self.add(tdef, dscfg, pstate, setupDelay=setupDelay)
        except Exception as e:
            self._logger.exception("tlm: load check_point: exception while adding download %s", tdef)