    def network_get_state(self, usercallback, getpeerlist):
        """ Called by network thread """
        with self.dllock:
            if self.handle is None:
                self._logger.debug("LibtorrentDownloadImpl: network_get_state: Download not running")
                if self.dlstate != DLSTATUS_CIRCUITS:
                    progress = self.progressbeforestop
                else:
                    tunnel_community = self.ltmgr.trsession.lm.tunnel_community
                    progress = tunnel_community.tunnels_ready(self.get_hops()) if tunnel_community else 1

                ds = DownloadState(self, self.dlstate, self.error, progress)
            else:
                (status, stats, seeding_stats, logmsgs) = self.network_get_stats(getpeerlist)
                ds = DownloadState(self, status, self.error, self.get_progress(), stats=stats,
                                   seeding_stats=seeding_stats, filepieceranges=self.filepieceranges, logmsgs=logmsgs)
                self.progressbeforestop = ds.get_progress()

            if usercallback:
                # Invoke the usercallback function via a new thread.
                # After the callback is invoked, the return values will be passed to the
                # returncallback for post-callback processing.
                if not self.done and self.session.lm.threadpool:
                    # runs on the reactor
                    def session_getstate_usercallback_target():
                        when, getpeerlist = usercallback(ds)
                        if when > 0.0:
                            # Schedule next invocation, either on general or DL specific
                            self.session.lm.threadpool.add_task(lambda: self.network_get_state(usercallback, getpeerlist), when)

                    self.session.lm.threadpool.add_task_in_thread(session_getstate_usercallback_target)
            else:
                return ds