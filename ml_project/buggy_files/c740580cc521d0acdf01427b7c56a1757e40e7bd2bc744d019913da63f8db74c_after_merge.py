  def _setup_paths(self, paths, filters=()):
    """Find interpreters under paths, and cache them."""
    for interpreter in self._matching(PythonInterpreter.all(paths), filters=filters):
      identity_str = str(interpreter.identity)
      pi = self._interpreter_from_relpath(identity_str, filters=filters)
      if pi is None:
        self._setup_interpreter(interpreter, identity_str)
        pi = self._interpreter_from_relpath(identity_str, filters=filters)
      if pi:
        yield pi