    def prepare(self):
        """Do initial preparation to run Python code.

        Includes finding the module to run, adjusting sys.argv[0], and changing
        sys.path to match what Python does.

        """
        should_update_sys_path = True

        if self.as_module:
            if env.PYBEHAVIOR.actual_syspath0_dash_m:
                path0 = os.getcwd()
            else:
                path0 = ""
            sys.path[0] = path0
            should_update_sys_path = False
            self.modulename = self.arg0
            pathname, self.package = find_module(self.modulename)
            self.pathname = os.path.abspath(pathname)
            self.args[0] = self.arg0 = self.pathname
        elif os.path.isdir(self.arg0):
            # Running a directory means running the __main__.py file in that
            # directory.
            path0 = self.arg0
            for ext in [".py", ".pyc", ".pyo"]:
                try_filename = os.path.join(self.arg0, "__main__" + ext)
                if os.path.exists(try_filename):
                    self.arg0 = try_filename
                    break
            else:
                raise NoSource("Can't find '__main__' module in '%s'" % self.arg0)
        else:
            path0 = os.path.abspath(os.path.dirname(self.arg0))

        if self.modulename is None and env.PYVERSION >= (3, 3):
            self.modulename = '__main__'

        if should_update_sys_path:
            # sys.path fakery.  If we are being run as a command, then sys.path[0]
            # is the directory of the "coverage" script.  If this is so, replace
            # sys.path[0] with the directory of the file we're running, or the
            # current directory when running modules.  If it isn't so, then we
            # don't know what's going on, and just leave it alone.
            top_file = inspect.stack()[-1][0].f_code.co_filename
            if os.path.abspath(sys.path[0]) == os.path.abspath(os.path.dirname(top_file)):
                # Set sys.path correctly.
                sys.path[0] = path0