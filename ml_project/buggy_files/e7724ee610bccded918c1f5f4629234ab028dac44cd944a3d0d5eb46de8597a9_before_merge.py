  def _pantsd_logging(self):
    """A context manager that runs with pantsd logging.

    Asserts that stdio (represented by file handles 0, 1, 2) is closed to ensure that
    we can safely reuse those fd numbers.
    """

    # Ensure that stdio is closed so that we can safely reuse those file descriptors.
    for fd in (0, 1, 2):
      try:
        os.fdopen(fd)
        raise AssertionError(
            'pantsd logging cannot initialize while stdio is open: {}'.format(fd))
      except OSError:
        pass

    # Redirect stdio to /dev/null for the rest of the run, to reserve those file descriptors
    # for further forks.
    with stdio_as(stdin_fd=-1, stdout_fd=-1, stderr_fd=-1):
      # Reinitialize logging for the daemon context.
      result = setup_logging(self._log_level, log_dir=self._log_dir, log_name=self.LOG_NAME)

      # Do a python-level redirect of stdout/stderr, which will not disturb `0,1,2`.
      # TODO: Consider giving these pipes/actual fds, in order to make them "deep" replacements
      # for `1,2`, and allow them to be used via `stdio_as`.
      sys.stdout = _LoggerStream(logging.getLogger(), logging.INFO, result.log_stream)
      sys.stderr = _LoggerStream(logging.getLogger(), logging.WARN, result.log_stream)

      self._logger.debug('logging initialized')
      yield result.log_stream