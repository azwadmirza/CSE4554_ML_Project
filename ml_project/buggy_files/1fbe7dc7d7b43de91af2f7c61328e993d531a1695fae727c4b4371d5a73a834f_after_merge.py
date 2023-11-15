    def __init__(self, source, path, argv):
        '''

        Args:
            source (str) : python source code

            path (str) : a filename to use in any debugging or error output

            argv (list[str]) : a list of string arguments to make available
                as ``sys.argv`` when the code executes

        '''
        self._permanent_error = None
        self._permanent_error_detail = None
        self.reset_run_errors()

        import ast
        self._code = None

        try:
            nodes = ast.parse(source, path)
            self._code = compile(nodes, filename=path, mode='exec', dont_inherit=True)
        except SyntaxError as e:
            import traceback
            self._code = None
            self._permanent_error = ("Invalid syntax in \"%s\" on line %d:\n%s" % (os.path.basename(e.filename), e.lineno, e.text))
            self._permanent_error_detail = traceback.format_exc()

        self._path = path
        self._source = source
        self._argv = argv
        self.ran = False