    def less(self, arg_s):
        """Show a file through the pager.

        Files ending in .py are syntax-highlighted."""
        if not arg_s:
            raise UsageError('Missing filename.')

        cont = open(arg_s).read()
        if arg_s.endswith('.py'):
            cont = self.shell.pycolorize(cont)
        page.page(cont)