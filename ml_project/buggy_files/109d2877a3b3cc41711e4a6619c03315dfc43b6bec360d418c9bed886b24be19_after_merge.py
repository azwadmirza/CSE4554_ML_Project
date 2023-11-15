    def __str__(self):
        try:
            pid = self.pid
            name = repr(self.name())
        except ZombieProcess:
            details = "(pid=%s (zombie))" % self.pid
        except NoSuchProcess:
            details = "(pid=%s (terminated))" % self.pid
        except AccessDenied:
            details = "(pid=%s)" % (self.pid)
        else:
            details = "(pid=%s, name=%s)" % (pid, name)
        return "%s.%s%s" % (self.__class__.__module__,
                            self.__class__.__name__, details)