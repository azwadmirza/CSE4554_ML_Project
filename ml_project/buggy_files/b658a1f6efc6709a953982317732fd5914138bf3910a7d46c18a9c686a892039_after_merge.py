  def _setup_cached(self, filters=()):
    """Find all currently-cached interpreters."""
    for interpreter_dir in os.listdir(self._cache_dir):
      pi = self._interpreter_from_relpath(interpreter_dir, filters=filters)
      if pi:
        logger.debug('Detected interpreter {}: {}'.format(pi.binary, str(pi.identity)))
        yield pi