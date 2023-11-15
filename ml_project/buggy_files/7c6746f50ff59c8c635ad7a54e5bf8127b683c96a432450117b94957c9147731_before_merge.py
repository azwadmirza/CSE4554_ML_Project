    def check_call(self, args, **kwargs):
        """Run a subprocess, make sure it exited with 0."""
        self.counter = track = self.counter + 1
        self.write("[{}] Running: {}".format(track, str_command(args)))
        if "input" not in kwargs and "stdin" not in kwargs:
            kwargs["stdin"] = DEVNULL
        span = self.command_span(track, args)
        process = self.launch_command(track, args, **kwargs)
        process.wait()
        spent = span.end()
        retcode = process.poll()
        if retcode:
            self.write(
                "[{}] exit {} in {:0.2f} secs.".format(track, retcode, spent)
            )
            raise CalledProcessError(retcode, args)
        self.write("[{}] ran in {:0.2f} secs.".format(track, spent))