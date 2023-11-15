    def write(self, message: str, prefix="TEL") -> None:
        """Write a message to the log."""
        if self.logfile.closed:
            return
        for sub_message in message.splitlines():
            line = "{:6.1f} {} | {}\n".format(
                time() - self.start_time, prefix, sub_message.rstrip()
            )
            self.logfile.write(line)
        self.logfile.flush()