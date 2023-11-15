    def communicate(self, input=None, timeout=None):
        """
        Interact with process and return its output and error.

        - Send *input* data to stdin.
        - Read data from stdout and stderr, until end-of-file is reached.
        - Wait for process to terminate.

        The optional *input* argument should be a
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
        if self._communicating_greenlets is None:
            self._communicating_greenlets = _CommunicatingGreenlets(self, input)
        greenlets = self._communicating_greenlets

        # If we were given stdin=stdout=stderr=None, we have no way to
        # communicate with the child, and thus no greenlets to wait
        # on. This is a nonsense case, but it comes up in the test
        # case for Python 3.5 (test_subprocess.py
        # RunFuncTestCase.test_timeout). Instead, we go directly to
        # self.wait
        if not greenlets and timeout is not None:
            self.wait(timeout=timeout, _raise_exc=True)

        done = joinall(greenlets, timeout=timeout)
        # Allow finished greenlets, if any, to raise. This takes priority over
        # the timeout exception.
        for greenlet in done:
            greenlet.get()
        if timeout is not None and len(done) != len(self._communicating_greenlets):
            raise TimeoutExpired(self.args, timeout)

        # Close only after we're sure that everything is done
        # (there was no timeout, or there was, but everything finished).
        # There should be no greenlets still running, even from a prior
        # attempt. If there are, then this can raise RuntimeError: 'reentrant call'.
        # So we ensure that previous greenlets are dead.
        for pipe in (self.stdout, self.stderr):
            if pipe:
                try:
                    pipe.close()
                except RuntimeError:
                    pass

        self.wait()

        return (None if greenlets.stdout is None else greenlets.stdout.get(),
                None if greenlets.stderr is None else greenlets.stderr.get())