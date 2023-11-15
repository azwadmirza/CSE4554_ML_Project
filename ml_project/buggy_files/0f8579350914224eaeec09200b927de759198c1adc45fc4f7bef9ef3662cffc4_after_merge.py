    def setup(self, dcfg=None, pstate=None, initialdlstatus=None,
              wrapperDelay=0, share_mode=False, checkpoint_disabled=False):
        """
        Create a Download object. Used internally by Session.
        @param dcfg DownloadStartupConfig or None (in which case
        a new DownloadConfig() is created and the result
        becomes the runtime config of this Download.
        :returns a Deferred to which a callback can be added which returns the result of
        network_create_engine_wrapper.
        """
        # Called by any thread, assume sessionlock is held
        self.handle_check_lc.start(1, now=False)
        self.set_checkpoint_disabled(checkpoint_disabled)

        try:
            # The deferred to be returned
            deferred = Deferred()
            with self.dllock:
                # Copy dlconfig, from default if not specified
                if dcfg is None:
                    cdcfg = DownloadStartupConfig()
                else:
                    cdcfg = dcfg
                self.dlconfig = cdcfg.dlconfig.copy()
                self.dlconfig.lock = self.dllock
                self.dlconfig.set_callback(self.dlconfig_changed_callback)

                if not isinstance(self.tdef, TorrentDefNoMetainfo):
                    self.set_corrected_infoname()
                    self.set_filepieceranges()

                self.dlstate = DLSTATUS_CIRCUITS if self.get_hops() > 0 else self.dlstate

                self._logger.debug(u"setup: initialdlstatus %s %s", hexlify(self.tdef.get_infohash()), initialdlstatus)

                def schedule_create_engine():
                    self.cew_scheduled = True
                    create_engine_wrapper_deferred = self.network_create_engine_wrapper(
                        self.pstate_for_restart, initialdlstatus, share_mode=share_mode)
                    create_engine_wrapper_deferred.chainDeferred(deferred)

                def schedule_create_engine_call(_):
                    self.register_task("schedule_create_engine",
                                       reactor.callLater(wrapperDelay, schedule_create_engine))

                # Add a lambda callback that ignored the parameter of the callback which schedules
                # a task using the taskamanger with wrapperDelay as delay.
                self.can_create_engine_wrapper().addCallback(schedule_create_engine_call)

            self.pstate_for_restart = pstate
            return deferred

        except Exception as e:
            with self.dllock:
                self.error = e
                print_exc()