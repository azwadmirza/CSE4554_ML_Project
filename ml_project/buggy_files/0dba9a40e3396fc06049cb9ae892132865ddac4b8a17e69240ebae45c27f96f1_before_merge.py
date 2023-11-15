    def launch_command(self, track, args, **kwargs) -> Popen:
        """Call a command, generate stamped, logged output."""
        kwargs = kwargs.copy()
        in_data = kwargs.get("input")
        if "input" in kwargs:
            del kwargs["input"]
            kwargs["stdin"] = PIPE
        kwargs["stdout"] = PIPE
        kwargs["stderr"] = STDOUT
        try:
            process = Popen(args, **kwargs)
        except OSError as exc:
            self.write("[{}] {}".format(track, exc))
            raise
        Popen([
            "stamp-telepresence", "--id",
            str(track), "--start-time",
            str(self.start_time)
        ],
              stdin=process.stdout,
              stdout=self.logfile,
              stderr=self.logfile)
        if in_data:
            process.communicate(in_data, timeout=kwargs.get("timeout"))
        return process