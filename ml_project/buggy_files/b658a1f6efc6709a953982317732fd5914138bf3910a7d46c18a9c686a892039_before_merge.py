  def _setup_cached(self, filters=()):
    """Find all currently-cached interpreters."""
    for interpreter_dir in os.listdir(self._cache_dir):
      path = os.path.join(self._cache_dir, interpreter_dir)
      if os.path.isdir(path):
        pi = self._interpreter_from_path(path, filters=filters)
        if pi:
          logger.debug('Detected interpreter {}: {}'.format(pi.binary, str(pi.identity)))
          yield pi