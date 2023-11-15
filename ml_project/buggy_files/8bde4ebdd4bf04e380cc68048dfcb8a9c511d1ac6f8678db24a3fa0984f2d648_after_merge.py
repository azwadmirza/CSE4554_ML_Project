    def _exec_file(self, fname):
        try:
            full_filename = filefind(fname, [u'.', self.ipython_dir])
        except IOError as e:
            self.log.warn("File not found: %r"%fname)
            return
        # Make sure that the running script gets a proper sys.argv as if it
        # were run from a system shell.
        save_argv = sys.argv
        sys.argv = [full_filename] + self.extra_args[1:]
        try:
            if os.path.isfile(full_filename):
                if full_filename.endswith('.ipy'):
                    self.log.info("Running file in user namespace: %s" %
                                  full_filename)
                    self.shell.safe_execfile_ipy(full_filename)
                else:
                    # default to python, even without extension
                    self.log.info("Running file in user namespace: %s" %
                                  full_filename)
                    # Ensure that __file__ is always defined to match Python behavior
                    self.shell.user_ns['__file__'] = fname
                    try:
                        self.shell.safe_execfile(full_filename, self.shell.user_ns)
                    finally:
                        del self.shell.user_ns['__file__']
        finally:
            sys.argv = save_argv