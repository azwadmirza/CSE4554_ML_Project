    def restart(self, initialdlstatus=None):
        """ Restart the Download """
        # Called by any thread
        self._logger.debug("LibtorrentDownloadImpl: restart: %s", self.tdef.get_name())

        with self.dllock:
            if self.handle is None:
                self.error = None

                def schedule_create_engine(_):
                    self.cew_scheduled = True
                    create_engine_wrapper_deferred = self.network_create_engine_wrapper(
                        self.pstate_for_restart, initialdlstatus, share_mode=self.get_share_mode())
                    create_engine_wrapper_deferred.addCallback(self.session.lm.on_download_handle_created)

                can_create_engine_deferred = self.can_create_engine_wrapper()
                can_create_engine_deferred.addCallback(schedule_create_engine)
            else:
                self.handle.resume()
                self.set_vod_mode(self.get_mode() == DLMODE_VOD)