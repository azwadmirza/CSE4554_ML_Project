    def process_flow(self, f):
        should_intercept = any(
            [
                self.state.intercept and flowfilter.match(self.state.intercept, f) and not f.request.is_replay,
                f.intercepted,
            ]
        )
        if should_intercept:
            f.intercept(self)
        signals.flowlist_change.send(self)
        signals.flow_change.send(self, flow=f)