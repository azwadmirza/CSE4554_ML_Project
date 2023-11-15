    def communicate(self, input=None, timeout=None):
        """Interact with process: Send data to stdin.  Read data from
        stdout and stderr, until end-of-file is reached.  Wait for
        process to terminate.  The optional input argument should be a
        string to be sent to the child process, or None, if no data
        should be sent to the child.

        communicate() returns a tuple (stdout, stderr).

        :keyword timeout: Under Python 2, this is a gevent extension; if
           given and it expires, we will raise :exc:`TimeoutExpired`, which
           extends :exc:`gevent.timeout.Timeout` (note that this only extends :exc:`BaseException`,
           *not* :exc:`Exception`)
           Under Python 3, this raises the standard :exc:`TimeoutExpired` exception.

        .. versionchanged:: 1.1a2
           Under Python 2, if the *timeout* elapses, raise the :exc:`gevent.timeout.Timeout`
           exception. Previously, we silently returned.
        .. versionchanged:: 1.1b5
           Honor a *timeout* even if there's no way to communicate with the child
           (stdin, stdout, and stderr are not pipes).
        """
        greenlets = []
        if self.stdin:
            greenlets.append(spawn(write_and_close, self.stdin, input))

        # If the timeout parameter is used, and the caller calls back after
        # getting a TimeoutExpired exception, we can wind up with multiple
        # greenlets trying to run and read from and close stdout/stderr.
        # That's bad because it can lead to 'RuntimeError: reentrant call in io.BufferedReader'.
        # We can't just kill the previous greenlets when a timeout happens,
        # though, because we risk losing the output collected by that greenlet
        # (and Python 3, where timeout is an official parameter, explicitly says
        # that no output should be lost in the event of a timeout.) Instead, we're
        # watching for the exception and ignoring it. It's not elegant,
        # but it works
        def _make_pipe_reader(pipe_name):
            pipe = getattr(self, pipe_name)
            buf_name = '_' + pipe_name + '_buffer'

            def _read():
                try:
                    data = pipe.read()
                except (
                        # io.Buffered* can raise RuntimeError: 'reentrant call'
                        RuntimeError,
                        # unbuffered Posix IO that we're already waiting on
                        # can raise this. Closing the pipe will free those greenlets up.
                        ConcurrentObjectUseError
                ):
                    return
                if not data:
                    return
                the_buffer = getattr(self, buf_name)
                if the_buffer:
                    the_buffer.append(data)
                else:
                    setattr(self, buf_name, [data])
            return _read

        if self.stdout:
            _read_out = _make_pipe_reader('stdout')
            stdout = spawn(_read_out)
            greenlets.append(stdout)
        else:
            stdout = None

        if self.stderr:
            _read_err = _make_pipe_reader('stderr')
            stderr = spawn(_read_err)
            greenlets.append(stderr)
        else:
            stderr = None

        # If we were given stdin=stdout=stderr=None, we have no way to
        # communicate with the child, and thus no greenlets to wait
        # on. This is a nonsense case, but it comes up in the test
        # case for Python 3.5 (test_subprocess.py
        # RunFuncTestCase.test_timeout). Instead, we go directly to
        # self.wait
        if not greenlets and timeout is not None:
            self.wait(timeout=timeout, _raise_exc=True)

        done = joinall(greenlets, timeout=timeout)
        if timeout is not None and len(done) != len(greenlets):
            raise TimeoutExpired(self.args, timeout)

        for pipe in (self.stdout, self.stderr):
            if pipe:
                try:
                    pipe.close()
                except RuntimeError:
                    pass

        self.wait()

        def _get_output_value(pipe_name):
            buf_name = '_' + pipe_name + '_buffer'
            buf_value = getattr(self, buf_name)
            setattr(self, buf_name, None)
            if buf_value:
                buf_value = self._communicate_empty_value.join(buf_value)
            else:
                buf_value = self._communicate_empty_value
            return buf_value

        stdout_value = _get_output_value('stdout')
        stderr_value = _get_output_value('stderr')

        return (None if stdout is None else stdout_value,
                None if stderr is None else stderr_value)