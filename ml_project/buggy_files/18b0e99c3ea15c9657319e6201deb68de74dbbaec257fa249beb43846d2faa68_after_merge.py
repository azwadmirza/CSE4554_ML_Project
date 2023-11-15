    def popen(self, args, **kwargs) -> Popen:
        """Return Popen object."""
        self.counter = track = self.counter + 1
        out_cb = err_cb = self.make_logger(track)

        def done(proc):
            self._popen_done(track, proc)

        self.write("[{}] Launching: {}".format(track, str_command(args)))
        process = self.launch_command(
            track, out_cb, err_cb, args, done=done, **kwargs
        )
        return process