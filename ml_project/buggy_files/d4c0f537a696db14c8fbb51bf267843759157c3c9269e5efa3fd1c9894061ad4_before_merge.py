    def communicate(self, input=None):
        """Interact with process: Send data to stdin.  Read data from
        stdout and stderr, until end-of-file is reached.  Wait for
        process to terminate.  The optional input argument should be a
        string to be sent to the child process, or None, if no data
        should be sent to the child.

        communicate() returns a tuple (stdout, stderr)."""
        greenlets = []
        if self.stdin:
            greenlets.append(spawn(write_and_close, self.stdin, input))

        if self.stdout:
            stdout = spawn(self.stdout.read)
            greenlets.append(stdout)
        else:
            stdout = None

        if self.stderr:
            stderr = spawn(self.stderr.read)
            greenlets.append(stderr)
        else:
            stderr = None

        joinall(greenlets)

        if self.stdout:
            self.stdout.close()
        if self.stderr:
            self.stderr.close()

        self.wait()
        return (None if stdout is None else stdout.value or '',
                None if stderr is None else stderr.value or '')