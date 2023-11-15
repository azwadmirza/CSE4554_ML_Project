    def launch_command(self, track, out_cb, err_cb, args, **kwargs) -> Popen:
        """Call a command, generate stamped, logged output."""
        try:
            process = launch_command(args, out_cb, err_cb, **kwargs)
        except OSError as exc:
            self.write("[{}] {}".format(track, exc))
            raise
        return process