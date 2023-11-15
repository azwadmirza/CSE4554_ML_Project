    def process_flow(self, f):
        if self.filt:
            should_intercept = all([
                self.filt(f),
                not f.is_replay == "request",
            ])
            if should_intercept and ctx.options.intercept_active:
                f.intercept()