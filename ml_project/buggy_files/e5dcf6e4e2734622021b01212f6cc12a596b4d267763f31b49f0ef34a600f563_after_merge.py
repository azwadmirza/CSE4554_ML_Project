    def __init_streams(self, stdin, stdout, stderr):
        self.stdin = self.stdout = self.stderr = None

        if stdin == PIPE:
            self._child_stdin, self._stdin = os.pipe()
            self.stdin = os.fdopen(self._stdin, 'wb')
        elif isinstance(stdin, int):
            self._child_stdin, self._stdin = stdin, -1
        elif stdin is not None:
            self._child_stdin, self._stdin = stdin.fileno(), -1
        else:
            self._child_stdin = self._stdin = -1

        if stdout == PIPE:
            self._stdout, self._child_stdout = os.pipe()
            self.stdout = os.fdopen(self._stdout, 'rb')
        elif isinstance(stdout, int):
            self._stdout, self._child_stdout = -1, stdout
        elif stdout is not None:
            self._stdout, self._child_stdout = -1, stdout.fileno()
        else:
            self._stdout = self._child_stdout = -1

        if stderr == PIPE:
            self._stderr, self._child_stderr = os.pipe()
            self.stderr = os.fdopen(self._stderr, 'rb')
        elif isinstance(stderr, int):
            self._stderr, self._child_stderr = -1, stderr
        elif stderr is not None:
            self._stderr, self._child_stderr = -1, stderr.fileno()
        else:
            self._stderr = self._child_stderr = -1