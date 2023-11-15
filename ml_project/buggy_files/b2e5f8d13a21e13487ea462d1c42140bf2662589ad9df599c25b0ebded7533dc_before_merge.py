    def communicate(self, input=None):
        # type: (Optional[bytes]) -> Tuple[bytes, bytes]
        """Communicates with the job sending any input data to stdin and collecting stdout and
        stderr.

        :param input: Data to send to stdin of the job as per the `subprocess` API.
        :return: A tuple of the job's stdout and stderr as per the `subprocess` API.
        :raises: :class:`Job.Error` if the job exited non-zero.
        """
        stdout, stderr = self._process.communicate(input=input)
        self._check_returncode(stderr)
        return stdout, stderr