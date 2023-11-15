        def sentry_start(self, *a, **kw):
            hub = Hub.current
            integration = hub.get_integration(ThreadingIntegration)
            if integration is not None:
                if not integration.propagate_hub:
                    hub_ = None
                else:
                    hub_ = Hub(hub)
                # Patching instance methods in `start()` creates a reference cycle if
                # done in a naive way. See
                # https://github.com/getsentry/sentry-python/pull/434
                #
                # In threading module, using current_thread API will access current thread instance
                # without holding it to avoid a reference cycle in an easier way.
                self.run = _wrap_run(hub_, self.run.__func__)

            return old_start(self, *a, **kw)  # type: ignore