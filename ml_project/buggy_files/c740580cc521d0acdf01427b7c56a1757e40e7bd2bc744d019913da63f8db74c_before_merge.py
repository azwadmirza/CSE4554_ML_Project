  def _setup_paths(self, paths, filters=()):
    """Find interpreters under paths, and cache them."""
    for interpreter in self._matching(PythonInterpreter.all(paths), filters=filters):
      identity_str = str(interpreter.identity)
      cache_path = os.path.join(self._cache_dir, identity_str)
      pi = self._interpreter_from_path(cache_path, filters=filters)
      if pi is None:
        self._setup_interpreter(interpreter, cache_path)
        pi = self._interpreter_from_path(cache_path, filters=filters)
      if pi:
        yield pi