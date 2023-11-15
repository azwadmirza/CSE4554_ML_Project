    def configure(self, updated):
        if "intercept" in updated:
            if not ctx.options.intercept:
                self.filt = None
                ctx.options.intercept_active = False
                return
            self.filt = flowfilter.parse(ctx.options.intercept)
            if not self.filt:
                raise exceptions.OptionsError(
                    "Invalid interception filter: %s" % ctx.options.intercept
                )
            ctx.options.intercept_active = True