                def schedule_create_engine(_):
                    self.cew_scheduled = True
                    create_engine_wrapper_deferred = self.network_create_engine_wrapper(
                        self.pstate_for_restart, initialdlstatus, share_mode=self.get_share_mode())
                    create_engine_wrapper_deferred.addCallback(self.session.lm.on_download_handle_created)