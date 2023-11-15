    def prepare(self):
        """Set sys.path properly.

        This needs to happen before any importing, and without importing anything.
        """
        should_update_sys_path = True
        if self.as_module:
            if env.PYBEHAVIOR.actual_syspath0_dash_m:
                path0 = os.getcwd()
            else:
                path0 = ""
            sys.path[0] = path0
            should_update_sys_path = False
        elif os.path.isdir(self.arg0):
            # Running a directory means running the __main__.py file in that
            # directory.
            path0 = self.arg0
        else:
            path0 = os.path.abspath(os.path.dirname(self.arg0))


        if should_update_sys_path:
            # sys.path fakery.  If we are being run as a command, then sys.path[0]
            # is the directory of the "coverage" script.  If this is so, replace
            # sys.path[0] with the directory of the file we're running, or the
            # current directory when running modules.  If it isn't so, then we
            # don't know what's going on, and just leave it alone.
            top_file = inspect.stack()[-1][0].f_code.co_filename
            if os.path.abspath(sys.path[0]) == os.path.abspath(os.path.dirname(top_file)):
                # Set sys.path correctly.
                sys.path[0] = python_reported_file(path0)