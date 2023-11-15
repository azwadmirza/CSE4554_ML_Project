    def get_output(self, args, reveal=False, **kwargs) -> str:
        """Return (stripped) command result as unicode string."""
        self.counter = track = self.counter + 1
        capture = []  # type: List[str]
        if reveal or self.verbose:
            out_cb = self.make_logger(track, capture=capture)
        else:
            out_cb = capture.append
        err_cb = self.make_logger(track)
        self.run_command(
            track, "Capturing", "captured", out_cb, err_cb, args, **kwargs
        )
        return "".join(capture).strip()