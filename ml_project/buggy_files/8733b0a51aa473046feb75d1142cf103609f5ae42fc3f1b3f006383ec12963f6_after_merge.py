    def less(self, arg_s):
        """Show a file through the pager.

        Files ending in .py are syntax-highlighted."""
        if not arg_s:
            raise UsageError('Missing filename.')

        cont = open(arg_s).read()
        if arg_s.endswith('.py'):
            cont = self.shell.pycolorize(openpy.read_py_file(arg_s, skip_encoding_cookie=False))
        else:
            cont = open(arg_s).read()
        page.page(cont)