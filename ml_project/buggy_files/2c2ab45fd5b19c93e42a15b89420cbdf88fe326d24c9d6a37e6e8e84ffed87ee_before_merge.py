                    def session_getstate_usercallback_target():
                        when, getpeerlist = usercallback(ds)
                        if when > 0.0 and self.session.lm.threadpool:
                            # Schedule next invocation, either on general or DL specific
                            self.session.lm.threadpool.add_task(lambda: self.network_get_state(usercallback, getpeerlist), when)