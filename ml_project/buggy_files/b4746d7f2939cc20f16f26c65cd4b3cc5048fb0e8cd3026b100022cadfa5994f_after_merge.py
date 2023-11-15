    def network_stop(self, removestate, removecontent):
        """ Called by network thread, but safe for any """
        with self.dllock:
            self._logger.debug("LibtorrentDownloadImpl: network_stop %s", self.tdef.get_name())
            self.cancel_all_pending_tasks()

            pstate = self.network_get_persistent_state()
            if self.handle is not None:
                self._logger.debug("LibtorrentDownloadImpl: network_stop: engineresumedata from torrent handle")
                self.pstate_for_restart = pstate
                if removestate:
                    self.ltmgr.remove_torrent(self, removecontent)
                    self.handle = None
                else:
                    self.set_vod_mode(False)
                    self.handle.pause()
                    self.save_resume_data()
            else:
                # This method is also called at Session shutdown, where one may
                # choose to checkpoint its Download. If the Download was
                # stopped before, pstate_for_restart contains its resumedata.
                # and that should be written into the checkpoint.
                #
                if self.pstate_for_restart is not None:
                    self._logger.debug(
                        "LibtorrentDownloadImpl: network_stop: Reusing previously saved engineresume data for checkpoint")
                    # Don't copy full pstate_for_restart, as the torrent
                    # may have gone from e.g. HASHCHECK at startup to STOPPED
                    # now, at shutdown. In other words, it was never active
                    # in this session and the pstate_for_restart still says
                    # HASHCHECK.
                    pstate.set('state', 'engineresumedata', self.pstate_for_restart.get('state', 'engineresumedata'))
                else:
                    self._logger.debug(
                        "LibtorrentDownloadImpl: network_stop: Could not reuse engineresumedata as pstart_for_restart is None")

            # Offload the removal of the dlcheckpoint to another thread
            if removestate:
                self.session.lm.remove_pstate(self.tdef.get_infohash())

            return (self.tdef.get_infohash(), pstate)