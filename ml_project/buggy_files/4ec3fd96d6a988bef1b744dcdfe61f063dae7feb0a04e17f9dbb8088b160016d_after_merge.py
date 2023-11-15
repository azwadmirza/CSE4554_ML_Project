    def wait(self, timeout=None):
        if timeout is None:
            cext_timeout = cext.INFINITE
        else:
            # WaitForSingleObject() expects time in milliseconds
            cext_timeout = int(timeout * 1000)
        while True:
            ret = cext.proc_wait(self.pid, cext_timeout)
            if ret == WAIT_TIMEOUT:
                raise TimeoutExpired(timeout, self.pid, self._name)
            if pid_exists(self.pid):
                if timeout is None:
                    continue
                else:
                    raise TimeoutExpired(timeout, self.pid, self._name)
            return ret