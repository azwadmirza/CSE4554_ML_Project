    def wrapper(self, *args, **kwargs):
        try:
            return wrap_exceptions(fun)(self)
        except NoSuchProcess:
            if not pid_exists(self.pid):
                raise
            else:
                raise ZombieProcess(self.pid, self._name)