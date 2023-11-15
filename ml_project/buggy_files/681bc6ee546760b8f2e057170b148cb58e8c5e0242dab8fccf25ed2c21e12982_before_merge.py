    def iterraw(self):
        """Iterates through the last stdout, and returns the lines
        exactly as found.
        """
        # get approriate handles
        proc = self.proc
        uninew = self.spec.universal_newlines
        # get the correct stdout
        stdout = proc.stdout
        if ((stdout is None or not safe_readable(stdout)) and
                self.spec.captured_stdout is not None):
            stdout = self.spec.captured_stdout
        if uninew and hasattr(stdout, 'buffer'):
            stdout = stdout.buffer
        if not stdout or not safe_readable(stdout):
            # we get here if the process is not bacgroundable or the
            # class is the real Popen
            wait_for_active_job()
            self._endtime()
            if self.captured == 'object':
                self.end(tee_output=False)
            raise StopIteration
        # get the correct stderr
        stderr = proc.stderr
        if ((stderr is None or not safe_readable(stderr)) and
                self.spec.captured_stderr is not None):
            stderr = self.spec.captured_stderr
        if uninew and hasattr(stderr, 'buffer'):
            stderr = stderr.buffer
        # read from process while it is running
        timeout = builtins.__xonsh_env__.get('XONSH_PROC_FREQUENCY')
        while proc.poll() is None:
            if getattr(proc, 'suspended', False):
                return
            elif getattr(proc, 'in_alt_mode', False):
                time.sleep(0.1)  # probably not leaving any time soon
                continue
            elif self._prev_procs_done():
                self._close_prev_procs()
                proc.prevs_are_closed = True
                break
            yield from safe_readlines(stdout, 1024)
            self.stream_stderr(safe_readlines(stderr, 1024))
            time.sleep(timeout)
        # read from process now that it is over
        yield from safe_readlines(stdout)
        self.stream_stderr(safe_readlines(stderr))
        proc.wait()
        self._endtime()
        yield from safe_readlines(stdout)
        self.stream_stderr(safe_readlines(stderr))
        if self.captured == 'object':
            self.end(tee_output=False)