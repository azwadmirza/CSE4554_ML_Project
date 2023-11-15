    def __enter__(self):
        """
        Prepare the namespace.
        """
        # Save previous __file__
        if self.ns_globals is None:
            if self.current_namespace:
                self.ns_globals, self.ns_locals = _get_globals_locals()
            else:
                ipython_shell = get_ipython()
                main_mod = ipython_shell.new_main_mod(
                    self.filename, '__main__')
                self.ns_globals = main_mod.__dict__
                self.ns_locals = None
                # Needed to allow pickle to reference main
                if '__main__' in sys.modules:
                    self._previous_main = sys.modules['__main__']
                sys.modules['__main__'] = main_mod
                self._reset_main = True
        if '__file__' in self.ns_globals:
            self._previous_filename = self.ns_globals['__file__']
        self.ns_globals['__file__'] = self.filename
        if (self._file_code is not None
                and not PY2
                and isinstance(self._file_code, bytes)):
            try:
                self._file_code = self._file_code.decode()
            except UnicodeDecodeError:
                # Setting the cache is not supported for non utf-8 files
                self._file_code = None
        if self._file_code is not None:
            # '\n' is used instead of the native line endings. (see linecache)
            # mtime is set to None to avoid a cache update.
            linecache.cache[self.filename] = (
                len(self._file_code), None,
                [line + '\n' for line in self._file_code.splitlines()],
                self.filename)
        return self.ns_globals, self.ns_locals