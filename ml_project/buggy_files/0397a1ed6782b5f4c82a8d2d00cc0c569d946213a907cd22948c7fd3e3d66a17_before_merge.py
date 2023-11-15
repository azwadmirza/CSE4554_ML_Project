    def _make_logger(
        self, track: int, do_log: bool, do_capture: bool, limit_capture=99999
    ) -> _Logger:
        """Create a logger that optionally captures what is logged"""
        prefix = "{:>3d}".format(track)

        def write(line: str):
            self.output.write(mask_sensitive_data(line), prefix=prefix)

        return _Logger(write, do_log, do_capture, limit_capture)