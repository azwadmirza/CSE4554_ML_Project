    def sesscb_states_callback(self, states_list):
        """
        This method is periodically (every second) called with a list of the download states of the active downloads.
        """
        self.state_cb_count += 1

        # Check to see if a download has finished
        new_active_downloads = []
        do_checkpoint = False
        seeding_download_list = []

        for ds in states_list:
            state = ds.get_status()
            download = ds.get_download()
            tdef = download.get_def()
            safename = tdef.get_name_as_unicode()

            if state == DLSTATUS_DOWNLOADING:
                new_active_downloads.append(safename)
            elif state == DLSTATUS_STOPPED_ON_ERROR:
                self._logger.error("Error during download: %s", repr(ds.get_error()))
                self.downloads.get(tdef.get_infohash()).stop()
                self.session.notifier.notify(NTFY_TORRENT, NTFY_ERROR, tdef.get_infohash(), repr(ds.get_error()))
            elif state == DLSTATUS_SEEDING:
                seeding_download_list.append({u'infohash': tdef.get_infohash(),
                                              u'download': download})

                if safename in self.previous_active_downloads:
                    self.session.notifier.notify(NTFY_TORRENT, NTFY_FINISHED, tdef.get_infohash(), safename)
                    do_checkpoint = True

                elif download.get_hops() == 0 and download.get_safe_seeding():
                    hops = self.session.config.get_default_number_hops()
                    self._logger.info("Moving completed torrent to tunneled session %d for hidden seeding %r",
                                      hops, download)
                    yield self.session.remove_download(download)

                    # copy the old download_config and change the hop count
                    dscfg = download.copy()
                    dscfg.set_hops(hops)

                    self.session.start_download_from_tdef(tdef, dscfg)

        self.previous_active_downloads = new_active_downloads
        if do_checkpoint:
            self.session.checkpoint_downloads()

        if self.state_cb_count % 4 == 0 and self.tunnel_community:
            self.tunnel_community.monitor_downloads(states_list)

        returnValue([])