    def network_create_engine_wrapper(self, pstate, checkpoint_disabled=False, share_mode=False, upload_mode=False):
        self.ltmgr = self.session.lm.ltmgr
        with self.dllock:
            self._logger.debug("LibtorrentDownloadImpl: network_create_engine_wrapper()")

            atp = {}
            atp["save_path"] = os.path.normpath(os.path.join(get_default_dest_dir(), self.get_dest_dir()))
            atp["storage_mode"] = lt.storage_mode_t.storage_mode_sparse
            atp["hops"] = self.get_hops()
            atp["flags"] = lt.add_torrent_params_flags_t.flag_paused | \
                           lt.add_torrent_params_flags_t.flag_duplicate_is_error | \
                           lt.add_torrent_params_flags_t.flag_update_subscribe

            if share_mode:
                atp["flags"] = atp["flags"] | lt.add_torrent_params_flags_t.flag_share_mode
            if upload_mode:
                atp["flags"] = atp["flags"] | lt.add_torrent_params_flags_t.flag_upload_mode

            self.set_checkpoint_disabled(checkpoint_disabled)

            resume_data = pstate.get('state', 'engineresumedata') if pstate else None
            if not isinstance(self.tdef, TorrentDefNoMetainfo):
                metainfo = self.tdef.get_metainfo()
                torrentinfo = lt.torrent_info(metainfo)

                self.orig_files = [file_entry.path.decode('utf-8') for file_entry in torrentinfo.files()]
                is_multifile = len(self.orig_files) > 1
                commonprefix = os.path.commonprefix(self.orig_files) if is_multifile else ''
                swarmname = commonprefix.partition(os.path.sep)[0]

                if is_multifile and swarmname != self.correctedinfoname:
                    for i, filename_old in enumerate(self.orig_files):
                        filename_new = os.path.join(self.correctedinfoname, filename_old[len(swarmname) + 1:])
                        # Path should be unicode if Libtorrent is using std::wstring (on Windows),
                        # else we use str (on Linux).
                        try:
                            torrentinfo.rename_file(i, filename_new)
                        except TypeError:
                            torrentinfo.rename_file(i, filename_new.encode("utf-8"))
                        self.orig_files[i] = filename_new

                atp["ti"] = torrentinfo
                if resume_data and isinstance(resume_data, dict):
                    # Rewrite save_path as a global path, if it is given as a relative path
                    if "save_path" in resume_data and not os.path.isabs(resume_data["save_path"]):
                        resume_data["save_path"] = six.text_type(
                            os.path.join(self.state_dir, ensure_unicode(resume_data["save_path"], 'utf-8')))
                    atp["resume_data"] = lt.bencode(resume_data)
            else:
                atp["url"] = self.tdef.get_url() or "magnet:?xt=urn:btih:" + hexlify(self.tdef.get_infohash())
                atp["name"] = self.tdef.get_name_as_unicode()

        def on_torrent_added(handle):
            self.handle = handle

            if self.handle and self.handle.is_valid():
                self.set_selected_files()

                user_stopped = pstate.get('download_defaults', 'user_stopped') if pstate else False

                # If we lost resume_data always resume download in order to force checking
                if not user_stopped or not resume_data:
                    self.handle.resume()

                    # If we only needed to perform checking, pause download after it is complete
                    self.pause_after_next_hashcheck = user_stopped

                self.set_vod_mode(self.get_mode() == DLMODE_VOD)

                # Limit the amount of connections if we have specified that
                self.handle.set_max_connections(self.session.config.get_libtorrent_max_conn_download())

                # Set limit on download for a bootstrap file
                if self.is_bootstrap_download:
                    self.handle.set_download_limit(self.session.config.get_bootstrap_max_download_rate())

                return self

        def on_torrent_failed(failure):
            self._logger.error("Could not add torrent to LibtorrentManager %s", self.tdef.get_name_as_unicode())

            self.cew_scheduled = False

            return Failure((self, pstate))

        return self.ltmgr.add_torrent(self, atp).addCallbacks(on_torrent_added, on_torrent_failed)