    def wrapper(self, *args, **kwargs):
        delay = 0.0001
        times = 33
        for x in range(times):  # retries for roughly 1 second
            try:
                return fun(self, *args, **kwargs)
            except WindowsError as _:
                err = _
                if err.winerror == ERROR_PARTIAL_COPY:
                    time.sleep(delay)
                    delay = min(delay * 2, 0.04)
                    continue
                else:
                    raise
        else:
            msg = "%s retried %s times, converted to AccessDenied as it's " \
                "still returning %r" % (fun, times, err)
            raise AccessDenied(pid=self.pid, name=self._name, msg=msg)