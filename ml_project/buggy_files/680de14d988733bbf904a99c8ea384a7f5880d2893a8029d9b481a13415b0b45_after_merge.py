    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Reset the namespace.
        """
        if self._previous_filename:
            self.ns_globals['__file__'] = self._previous_filename
        elif '__file__' in self.ns_globals:
            self.ns_globals.pop('__file__')

        if not self.current_namespace:
            _set_globals_locals(self.ns_globals, self.ns_locals)

        if self._previous_main:
            sys.modules['__main__'] = self._previous_main
        elif '__main__' in sys.modules and self._reset_main:
            del sys.modules['__main__']
        if self.filename in linecache.cache:
            linecache.cache.pop(self.filename)