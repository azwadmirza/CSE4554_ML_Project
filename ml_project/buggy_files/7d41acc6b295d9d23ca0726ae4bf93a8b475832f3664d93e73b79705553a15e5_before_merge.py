    def get_output(self, args, reveal=False, stderr=None, **kwargs) -> str:
        """Return (stripped) command result as unicode string."""
        if stderr is None:
            stderr = self.logfile
        self.counter = track = self.counter + 1
        self.write("[{}] Capturing: {}".format(track, str_command(args)))
        kwargs["stdin"] = DEVNULL
        kwargs["stderr"] = stderr
        span = self.command_span(track, args)
        try:
            result = str(check_output(args, **kwargs).strip(), "utf-8")
        finally:
            spent = span.end()
            if reveal or self.verbose:
                self.write(result, prefix="{:3d}".format(track))
        if spent > 1:
            self.write("[{}] captured in {:0.2f} secs.".format(track, spent))
        return result