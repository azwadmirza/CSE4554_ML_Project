    def as_instanceof_cause(self):
        """Returns copy that is an instance of the cause's Python class.

        The returned exception will inherit from both RayTaskError and the
        cause class.
        """

        if issubclass(RayTaskError, self.cause_cls):
            return self  # already satisfied

        if issubclass(self.cause_cls, RayError):
            return self  # don't try to wrap ray internal errors

        class cls(RayTaskError, self.cause_cls):
            def __init__(self, function_name, traceback_str, cause_cls,
                         proctitle, pid, ip):
                RayTaskError.__init__(self, function_name, traceback_str,
                                      cause_cls, proctitle, pid, ip)

        name = "RayTaskError({})".format(self.cause_cls.__name__)
        cls.__name__ = name
        cls.__qualname__ = name

        return cls(self.function_name, self.traceback_str, self.cause_cls,
                   self.proctitle, self.pid, self.ip)