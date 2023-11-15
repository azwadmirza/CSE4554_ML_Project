    def default(self, line):
        """
        Default way of running pdb statment.

        The only difference with Pdb.default is that if line contains multiple
        statments, the code will be compiled with 'exec'. It will not print the
        result but will run without failing.
        """
        execute_events = self.pdb_execute_events
        if line[:1] == '!':
            line = line[1:]
        # Disallow the use of %debug magic in the debugger
        if line.startswith("%debug"):
            self.error("Please don't use '%debug' in the debugger.\n"
                       "For a recursive debugger, use the pdb 'debug'"
                       " command instead")
            return
        locals = self.curframe_locals
        globals = self.curframe.f_globals
        try:
            line = TransformerManager().transform_cell(line)
            try:
                code = compile(line + '\n', '<stdin>', 'single')
            except SyntaxError:
                # support multiline statments
                code = compile(line + '\n', '<stdin>', 'exec')
            save_stdout = sys.stdout
            save_stdin = sys.stdin
            save_displayhook = sys.displayhook
            try:
                sys.stdin = self.stdin
                sys.stdout = self.stdout
                sys.displayhook = self.displayhook
                if execute_events:
                     get_ipython().events.trigger('pre_execute')
                exec(code, globals, locals)
                if execute_events:
                     get_ipython().events.trigger('post_execute')
            finally:
                sys.stdout = save_stdout
                sys.stdin = save_stdin
                sys.displayhook = save_displayhook
        except BaseException:
            if PY2:
                t, v = sys.exc_info()[:2]
                if type(t) == type(''):
                    exc_type_name = t
                else: exc_type_name = t.__name__
                print >>self.stdout, '***', exc_type_name + ':', v
            else:
                exc_info = sys.exc_info()[:2]
                self.error(
                    traceback.format_exception_only(*exc_info)[-1].strip())