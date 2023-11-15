    def sesscb_states_callback(self, dslist):
        if not self.ready:
            return 5.0, []

        # update tray icon
        total_download, total_upload = get_download_upload_speed(dslist)
        if self.frame and self.frame.tbicon:
            self.frame.tbicon.updateTooltip(total_download, total_upload)

        wantpeers = []
        self.ratestatecallbackcount += 1
        try:
            # Print stats on Console
            if self.ratestatecallbackcount % 5 == 0:
                for ds in dslist:
                    safename = repr(ds.get_download().get_def().get_name())
                    self._logger.debug(
                        "%s %s %.1f%% dl %.1f ul %.1f n %d",
                        safename,
                        dlstatus_strings[ds.get_status()],
                        100.0 * ds.get_progress(),
                        ds.get_current_speed(DOWNLOAD),
                        ds.get_current_speed(UPLOAD),
                        ds.get_num_peers())
                    if ds.get_status() == DLSTATUS_STOPPED_ON_ERROR:
                        self._logger.error("main: Error: %s", repr(ds.get_error()))
                        download = self.utility.session.lm.downloads.get(ds.get_infohash())
                        if download:
                            download.stop()

                        # show error dialog
                        dlg = wx.MessageDialog(self.frame,
                                               "Download stopped on error: %s" % repr(ds.get_error()),
                                               "Download Error",
                                               wx.OK | wx.ICON_ERROR)
                        dlg.ShowModal()
                        dlg.Destroy()

            # Pass DownloadStates to libaryView
            no_collected_list = [ds for ds in dslist]
            try:
                # Arno, 2012-07-17: Retrieving peerlist for the DownloadStates takes CPU
                # so only do it when needed for display.
                wantpeers.extend(self.guiUtility.library_manager.download_state_callback(no_collected_list))
            except:
                print_exc()

            # Check to see if a download has finished
            newActiveDownloads = []
            doCheckpoint = False
            seeding_download_list = []
            for ds in dslist:
                state = ds.get_status()
                download = ds.get_download()
                tdef = download.get_def()
                safename = tdef.get_name_as_unicode()

                if state == DLSTATUS_DOWNLOADING:
                    newActiveDownloads.append(safename)

                elif state == DLSTATUS_SEEDING:
                    seeding_download_list.append({u'infohash': tdef.get_infohash(),
                                                  u'download': download,
                                                  })

                    if safename in self.prevActiveDownloads:
                        infohash = tdef.get_infohash()

                        self.utility.session.notifier.notify(NTFY_TORRENTS, NTFY_FINISHED, infohash, safename)

                        doCheckpoint = True

                    elif download.get_hops() == 0 and download.get_safe_seeding():
                        hops = self.utility.read_config('default_number_hops')
                        self._logger.info("Moving completed torrent to tunneled session %d for hidden sedding %r",
                                          hops, download)
                        self.utility.session.remove_download(download)

                        # copy the old download_config and change the hop count
                        dscfg = download.copy()
                        dscfg.set_hops(hops)

                        # TODO(emilon): That's a hack to work around the fact
                        # that removing a torrent is racy.
                        def schedule_download():
                            self.register_task(
                                "reschedule_dowload", reactor.callLater(5,
                                                                        reactor.callInThread,
                                                                        self.utility.session.start_download_from_tdef,
                                                                        tdef, dscfg))

                        reactor.callFromThread(schedule_download)

            self.prevActiveDownloads = newActiveDownloads
            if doCheckpoint:
                self.utility.session.checkpoint()

            if self.utility.read_config(u'seeding_mode') == 'never':
                for data in seeding_download_list:
                    data[u'download'].stop()
                    self.utility.session.tribler_config.set_download_state(data[u'infohash'], "stop")

            # Adjust speeds and call TunnelCommunity.monitor_downloads once every 4 seconds
            adjustspeeds = False
            if self.ratestatecallbackcount % 4 == 0:
                adjustspeeds = True

            if adjustspeeds and self.tunnel_community:
                self.tunnel_community.monitor_downloads(dslist)

        except:
            print_exc()

        return 1.0, wantpeers