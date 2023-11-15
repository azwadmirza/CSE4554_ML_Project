    def __exit__(self, exc_type, exc_value, traceback):
        self.close(force=True)
        # Wait for the process to terminate, to avoid zombies.
        self.wait()