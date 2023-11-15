    def execute(self, cmd, persist=False, timeout=DEFAULT_TIMEOUT, timeout_check_interval=DEFAULT_TIMEOUT_CHECK_INTERVAL, **kwds):
        outf = TemporaryFile()
        p = Popen(cmd, stdin=None, stdout=outf, stderr=PIPE)
        # poll until timeout

        for i in range(int(timeout / timeout_check_interval)):
            sleep(0.1)  # For fast returning commands
            r = p.poll()
            if r is not None:
                break
            sleep(timeout_check_interval)
        else:
            kill_pid(p.pid)
            return Bunch(stdout=u'', stderr=TIMEOUT_ERROR_MESSAGE, returncode=TIMEOUT_RETURN_CODE)
        outf.seek(0)
        return Bunch(stdout=_read_str(outf), stderr=_read_str(p.stderr), returncode=p.returncode)