    def network_create_engine_wrapper(self, pstate, initialdlstatus=None, checkpoint_disabled=False, share_mode=False):
        with self.dllock:
            self._logger.debug("LibtorrentDownloadImpl: network_create_engine_wrapper()")

            atp = {}
            atp["save_path"] = os.path.abspath(self.get_dest_dir())
            atp["storage_mode"] = lt.storage_mode_t.storage_mode_sparse
            atp["paused"] = True
            atp["auto_managed"] = False
            atp["duplicate_is_error"] = True
            atp["hops"] = self.get_hops()

            if share_mode:
                atp["flags"] = lt.add_torrent_params_flags_t.flag_share_mode

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
                has_resume_data = resume_data and isinstance(resume_data, dict)
                if has_resume_data:
                    atp["resume_data"] = lt.bencode(resume_data)
            else:
                atp["url"] = self.tdef.get_url() or "magnet:?xt=urn:btih:" + hexlify(self.tdef.get_infohash())
                atp["name"] = self.tdef.get_name_as_unicode()

            self.handle = self.ltmgr.add_torrent(self, atp)
            # assert self.handle.status().share_mode == share_mode
            if self.handle.is_valid():

                self.set_selected_files()

                # If we lost resume_data always resume download in order to force checking
                if initialdlstatus != DLSTATUS_STOPPED or not resume_data:
                    self.handle.resume()

                    # If we only needed to perform checking, pause download after it is complete
                    self.pause_after_next_hashcheck = initialdlstatus == DLSTATUS_STOPPED

                if self.get_mode() == DLMODE_VOD:
                    self.set_vod_mode(True)

                # Limit the amount of connections if we have specified that
                if self.session.get_libtorrent_max_conn_download() != -1:
                    self.handle.set_max_connections(max(2, self.session.get_libtorrent_max_conn_download()))

                self.handle.resolve_countries(True)

            else:
                self._logger.error("Could not add torrent to LibtorrentManager %s", self.tdef.get_name_as_unicode())

                self.cew_scheduled = False

                # Return a deferred with the errback already being called
                return defer.fail((self, pstate))

            self.cew_scheduled = False

            # Return a deferred with the callback already being called
            return defer.succeed(self)