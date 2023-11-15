    def wait(self):
        # type: () -> None
        """Waits for the job to complete.

        :raises: :class:`Job.Error` if the job exited non-zero.
        """
        self._process.wait()
        self._check_returncode()