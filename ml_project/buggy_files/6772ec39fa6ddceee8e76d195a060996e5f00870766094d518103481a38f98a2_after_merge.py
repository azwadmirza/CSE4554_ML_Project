    def process_flow(self, f: flow.Flow) -> None:
        if self.should_intercept(f):
            assert f.reply
            if f.reply.state != "start":
                return ctx.log.debug("Cannot intercept request that is already taken by another addon.")
            f.intercept()