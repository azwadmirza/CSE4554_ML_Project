    def close(self):
        try:
            if self.json:
                sys.stdout.write('{"fetch":"%s","finished":true,"maxval":1,"progress":1}\n\0'
                                 % self.description)
                sys.stdout.flush()
            elif self.enabled:
                self.pbar.close()
        except (IOError, OSError) as e:
            # Ignore BrokenPipeError and errors related to stdout or stderr being
            # closed by a downstream program.
            if e.errno not in (EPIPE, ESHUTDOWN):
                raise
        self.enabled = False