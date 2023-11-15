  def _CheckStatusWorkerProcess(self, pid):
    """Checks the status of a worker process.

    If a worker process is not responding the process is terminated and
    a replacement process is started.

    Args:
      pid (int): process ID (PID) of a registered worker process.

    Raises:
      KeyError: if the process is not registered with the engine.
    """
    # TODO: Refactor this method, simplify and separate concerns (monitoring
    # vs management).
    self._RaiseIfNotRegistered(pid)

    process = self._processes_per_pid[pid]

    process_status = self._GetProcessStatus(process)
    if process_status is None:
      process_is_alive = False
    else:
      process_is_alive = True

    process_information = self._process_information_per_pid[pid]
    used_memory = process_information.GetUsedMemory() or 0

    if used_memory > self._worker_memory_limit:
      logging.warning((
          u'Process: {0:s} (PID: {1:d}) killed because it exceeded the '
          u'memory limit: {2:d}.').format(
              process.name, pid, self._worker_memory_limit))
      self._KillProcess(pid)

    if isinstance(process_status, dict):
      self._rpc_errors_per_pid[pid] = 0
      status_indicator = process_status.get(u'processing_status', None)

    else:
      rpc_errors = self._rpc_errors_per_pid.get(pid, 0) + 1
      self._rpc_errors_per_pid[pid] = rpc_errors

      if rpc_errors > self._MAXIMUM_RPC_ERRORS:
        process_is_alive = False

      if process_is_alive:
        rpc_port = process.rpc_port.value
        logging.warning((
            u'Unable to retrieve process: {0:s} (PID: {1:d}) status via '
            u'RPC socket: http://localhost:{2:d}').format(
                process.name, pid, rpc_port))

        processing_status_string = u'RPC error'
        status_indicator = definitions.PROCESSING_STATUS_RUNNING
      else:
        processing_status_string = u'killed'
        status_indicator = definitions.PROCESSING_STATUS_KILLED

      process_status = {
          u'processing_status': processing_status_string}

    self._UpdateProcessingStatus(pid, process_status, used_memory)

    if status_indicator in definitions.PROCESSING_ERROR_STATUS:
      logging.error((
          u'Process {0:s} (PID: {1:d}) is not functioning correctly. '
          u'Status code: {2!s}.').format(process.name, pid, status_indicator))

      self._TerminateProcess(pid)

      logging.info(u'Starting replacement worker process for {0:s}'.format(
          process.name))
      replacement_process = self._StartWorkerProcess(self._storage_writer)
      self._StartMonitoringProcess(replacement_process.pid)