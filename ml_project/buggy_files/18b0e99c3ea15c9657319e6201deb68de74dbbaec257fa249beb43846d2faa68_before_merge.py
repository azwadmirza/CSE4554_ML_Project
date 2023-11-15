    def popen(self, args, stdin=DEVNULL, **kwargs) -> Popen:
        """Return Popen object."""
        self.counter = track = self.counter + 1
        self.write("[{}] Launching: {}".format(track, str_command(args)))
        kwargs["stdin"] = stdin
        result = self.launch_command(track, args, **kwargs)
        return result