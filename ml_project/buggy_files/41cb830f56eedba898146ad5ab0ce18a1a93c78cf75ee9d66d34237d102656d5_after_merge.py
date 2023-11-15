    def safe_execfile(self, fname, *where, **kw):
        """A safe version of the builtin execfile().

        This version will never throw an exception, but instead print
        helpful error messages to the screen.  This only works on pure
        Python files with the .py extension.

        Parameters
        ----------
        fname : string
            The name of the file to be executed.
        where : tuple
            One or two namespaces, passed to execfile() as (globals,locals).
            If only one is given, it is passed as both.
        exit_ignore : bool (False)
            If True, then silence SystemExit for non-zero status (it is always
            silenced for zero status, as it is so common).
        raise_exceptions : bool (False)
            If True raise exceptions everywhere. Meant for testing.

        """
        kw.setdefault('exit_ignore', False)
        kw.setdefault('raise_exceptions', False)

        fname = os.path.abspath(os.path.expanduser(fname))

        # Make sure we can open the file
        try:
            with open(fname) as thefile:
                pass
        except:
            warn('Could not open file <%s> for safe execution.' % fname)
            return

        # Find things also in current directory.  This is needed to mimic the
        # behavior of running a script from the system command line, where
        # Python inserts the script's directory into sys.path
        dname = os.path.dirname(fname)

        with prepended_to_syspath(dname):
            try:
                py3compat.execfile(fname,*where)
            except SystemExit as status:
                # If the call was made with 0 or None exit status (sys.exit(0)
                # or sys.exit() ), don't bother showing a traceback, as both of
                # these are considered normal by the OS:
                # > python -c'import sys;sys.exit(0)'; echo $?
                # 0
                # > python -c'import sys;sys.exit()'; echo $?
                # 0
                # For other exit status, we show the exception unless
                # explicitly silenced, but only in short form.
                if kw['raise_exceptions']:
                    raise
                if status.code and not kw['exit_ignore']:
                    self.showtraceback(exception_only=True)
            except:
                if kw['raise_exceptions']:
                    raise
                # tb offset is 2 because we wrap execfile
                self.showtraceback(tb_offset=2)