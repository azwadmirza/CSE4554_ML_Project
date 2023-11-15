  def _setup_interpreter(self, interpreter, cache_target_path):
    with safe_concurrent_creation(cache_target_path) as safe_path:
      os.mkdir(safe_path)  # Parent will already have been created by safe_concurrent_creation.
      os.symlink(interpreter.binary, os.path.join(safe_path, 'python'))
      return self._resolve(interpreter, safe_path)