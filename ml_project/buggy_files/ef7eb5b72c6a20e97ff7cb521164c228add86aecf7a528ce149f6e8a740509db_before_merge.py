    def tcp_message(self, f):
        if self.filt and ctx.options.intercept_active:
            f.intercept()