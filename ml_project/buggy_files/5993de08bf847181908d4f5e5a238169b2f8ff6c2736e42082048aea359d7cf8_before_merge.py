    def __init__(self, compiler, element_type):
        super(UnsupportedCompilationError, self).__init__(
            "Compiler %r can't render element of type %s"
            % (compiler, element_type)
        )