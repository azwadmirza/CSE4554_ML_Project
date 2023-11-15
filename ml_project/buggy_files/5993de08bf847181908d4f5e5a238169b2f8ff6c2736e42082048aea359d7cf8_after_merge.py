    def __init__(self, compiler, element_type, message=None):
        super(UnsupportedCompilationError, self).__init__(
            "Compiler %r can't render element of type %s%s"
            % (compiler, element_type, ": %s" % message if message else "")
        )