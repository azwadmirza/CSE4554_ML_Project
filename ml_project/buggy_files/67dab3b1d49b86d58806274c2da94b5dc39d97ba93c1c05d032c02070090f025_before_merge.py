    def wrapper(self, *args, **kwargs):
        try:
            return fun(self, *args, **kwargs)
        except OSError as err:
            raise convert_oserror(err, pid=self.pid, name=self._name)