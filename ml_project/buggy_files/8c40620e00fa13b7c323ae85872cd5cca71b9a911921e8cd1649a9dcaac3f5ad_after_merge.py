  def _run_pants_with_retry(self, pantsd_handle, retries=3):
    """Runs pants remotely with retry and recovery for nascent executions.

    :param PantsDaemon.Handle pantsd_handle: A Handle for the daemon to connect to.
    """
    attempt = 1
    while 1:
      logger.debug(
        'connecting to pantsd on port {} (attempt {}/{})'
        .format(pantsd_handle.port, attempt, retries)
      )
      try:
        return self._connect_and_execute(pantsd_handle)
      except self.RECOVERABLE_EXCEPTIONS as e:
        if attempt > retries:
          raise self.Fallback(e)

        self._backoff(attempt)
        logger.warn(
          'pantsd was unresponsive on port {}, retrying ({}/{})'
          .format(pantsd_handle.port, attempt, retries)
        )

        # One possible cause of the daemon being non-responsive during an attempt might be if a
        # another lifecycle operation is happening concurrently (incl teardown). To account for
        # this, we won't begin attempting restarts until at least 1 second has passed (1 attempt).
        if attempt > 1:
          pantsd_handle = self._restart_pantsd()
        attempt += 1
      except NailgunClient.NailgunError as e:
        # Ensure a newline.
        logger.fatal('')
        logger.fatal('lost active connection to pantsd!')
        raise_with_traceback(self._extract_remote_exception(pantsd_handle.pid, e))