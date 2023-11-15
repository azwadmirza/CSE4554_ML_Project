    def __init__(self, source, path, argv):
        self._failed = False
        self._error = None
        self._error_detail = None

        import ast
        self._code = None

        try:
            nodes = ast.parse(source, path)
            self._code = compile(nodes, filename=path, mode='exec')
        except SyntaxError as e:
            self._failed = True
            self._error = ("Invalid syntax in \"%s\" on line %d:\n%s" % (os.path.basename(e.filename), e.lineno, e.text))
            import traceback
            self._error_detail = traceback.format_exc()

        self._path = path
        self._source = source
        self._argv = argv
        self.ran = False