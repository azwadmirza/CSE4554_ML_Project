    def __init__(self, argument: Exception):
        if type(argument) is type and issubclass(argument, Exception):
            message = "pipeline failed - %s" % traceback.format_exc(argument)
        else:
            message = "pipeline failed - %s" % repr(argument)
        super().__init__(message)