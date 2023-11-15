    def check_call(self, args, **kwargs):
        """Run a subprocess, make sure it exited with 0."""
        self.counter = track = self.counter + 1
        out_cb = err_cb = self.make_logger(track)
        self.run_command(
            track, "Running", "ran", out_cb, err_cb, args, **kwargs
        )