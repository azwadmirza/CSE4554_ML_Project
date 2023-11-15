    def resume_download(self, filename, initialdlstatus=None, initialdlstatus_dict={}, setupDelay=0):
        tdef = dscfg = pstate = None

        try:
            pstate = self.load_download_pstate(filename)

            # SWIFTPROC
            metainfo = pstate.get('state', 'metainfo')
            if 'infohash' in metainfo:
                tdef = TorrentDefNoMetainfo(metainfo['infohash'], metainfo['name'], metainfo.get('url', None))
            else:
                tdef = TorrentDef.load_from_dict(metainfo)

            if pstate.has_option('downloadconfig', 'saveas') and \
                    isinstance(pstate.get('downloadconfig', 'saveas'), tuple):
                pstate.set('downloadconfig', 'saveas', pstate.get('downloadconfig', 'saveas')[-1])

            dscfg = DownloadStartupConfig(pstate)

        except:
            # pstate is invalid or non-existing
            _, file = os.path.split(filename)

            infohash = binascii.unhexlify(file[:-6])

            torrent_data = self.torrent_store.get(infohash)
            if torrent_data:
                tdef = TorrentDef.load_from_memory(torrent_data)

                defaultDLConfig = DefaultDownloadStartupConfig.getInstance()
                dscfg = defaultDLConfig.copy()

                if self.mypref_db is not None:
                    dest_dir = self.mypref_db.getMyPrefStatsInfohash(infohash)
                    if dest_dir:
                        if os.path.isdir(dest_dir) or dest_dir == '':
                            dscfg.set_dest_dir(dest_dir)

        self._logger.debug("tlm: load_checkpoint: pstate is %s %s",
                           pstate.get('dlstate', 'status'), pstate.get('dlstate', 'progress'))
        if pstate.get('state', 'engineresumedata') is None:
            self._logger.debug("tlm: load_checkpoint: resumedata None")
        else:
            self._logger.debug("tlm: load_checkpoint: resumedata len %d", len(pstate.get('state', 'engineresumedata')))

        if tdef and dscfg:
            if dscfg.get_dest_dir() != '':  # removed torrent ignoring
                try:
                    if not self.download_exists(tdef.get_infohash()):
                        initialdlstatus = initialdlstatus_dict.get(tdef.get_infohash(), initialdlstatus)
                        self.add(tdef, dscfg, pstate, initialdlstatus, setupDelay=setupDelay)
                    else:
                        self._logger.info("tlm: not resuming checkpoint because download has already been added")

                except Exception as e:
                    self._logger.exception("tlm: load check_point: exception while adding download %s", tdef)
            else:
                self._logger.info("tlm: removing checkpoint %s destdir is %s", filename, dscfg.get_dest_dir())
                os.remove(filename)
        else:
            self._logger.info("tlm: could not resume checkpoint %s %s %s", filename, tdef, dscfg)