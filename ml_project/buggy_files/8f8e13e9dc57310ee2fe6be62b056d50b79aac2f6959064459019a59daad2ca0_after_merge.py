    def prepare(self):
        """Set sys.path properly.

        This needs to happen before any importing, and without importing anything.
        """
        if self.as_module:
            if env.PYBEHAVIOR.actual_syspath0_dash_m:
                path0 = os.getcwd()
            else:
                path0 = ""
        elif os.path.isdir(self.arg0):
            # Running a directory means running the __main__.py file in that
            # directory.
            path0 = self.arg0
        else:
            path0 = os.path.abspath(os.path.dirname(self.arg0))

        if os.path.isdir(sys.path[0]):
            # sys.path fakery.  If we are being run as a command, then sys.path[0]
            # is the directory of the "coverage" script.  If this is so, replace
            # sys.path[0] with the directory of the file we're running, or the
            # current directory when running modules.  If it isn't so, then we
            # don't know what's going on, and just leave it alone.
            top_file = inspect.stack()[-1][0].f_code.co_filename
            sys_path_0_abs = os.path.abspath(sys.path[0])
            top_file_dir_abs = os.path.abspath(os.path.dirname(top_file))
            sys_path_0_abs = canonical_filename(sys_path_0_abs)
            top_file_dir_abs = canonical_filename(top_file_dir_abs)
            if sys_path_0_abs != top_file_dir_abs:
                path0 = None

        else:
            # sys.path[0] is a file. Is the next entry the directory containing
            # that file?
            if sys.path[1] == os.path.dirname(sys.path[0]):
                # Can it be right to always remove that?
                del sys.path[1]

        if path0 is not None:
            sys.path[0] = python_reported_file(path0)