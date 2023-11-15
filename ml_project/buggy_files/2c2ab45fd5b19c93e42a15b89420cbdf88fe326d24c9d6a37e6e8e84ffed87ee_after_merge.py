                    def session_getstate_usercallback_target():
                        when, getpeerlist = usercallback(ds)
                        if when > 0.0 and not self.session.lm.shutdownstarttime:
                            # Schedule next invocation, either on general or DL specific
                            def reschedule_cb():
                                dc = reactor.callLater(when, lambda: self.network_get_state(usercallback, getpeerlist))
                                self.register_task("downloads_cb", dc)

                            reactor.callFromThread(reschedule_cb)