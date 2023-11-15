    def configure(self, updated):
        if "intercept" in updated:
            if ctx.options.intercept:
                self.filt = flowfilter.parse(ctx.options.intercept)
                if not self.filt:
                    raise exceptions.OptionsError(f"Invalid interception filter: {ctx.options.intercept}")
                ctx.options.intercept_active = True
            else:
                self.filt = None
                ctx.options.intercept_active = False