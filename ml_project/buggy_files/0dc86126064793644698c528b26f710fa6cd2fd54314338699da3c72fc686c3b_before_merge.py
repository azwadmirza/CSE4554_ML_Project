        def sentry_start(self, *a, **kw):
            hub = Hub.current
            integration = hub.get_integration(ThreadingIntegration)
            if integration is not None:
                if not integration.propagate_hub:
                    hub_ = None
                else:
                    hub_ = Hub(hub)

                self.run = _wrap_run(hub_, self.run)

            return old_start(self, *a, **kw)  # type: ignore