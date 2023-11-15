  def _CheckProcessStatus(self, pid):
    """Check status of a specific monitored process and take action on it.

    This method examines the status of a process, and then terminates it,
    signals other processes to terminate or starts a replacement process as
    appropriate.

    Args:
      pid: The process ID (PID).

    Raises:
      EngineAbort: when the collector or storage worker process
                   unexpectedly terminated.
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
          u'processing_status': processing_status_string,
          u'type': process.type,
      }

    if status_indicator == definitions.PROCESSING_STATUS_ERROR:
      path_spec = process_status.get(u'path_spec', None)
      if path_spec:
        self._processing_status.error_path_specs.append(path_spec)

    self._UpdateProcessingStatus(pid, process_status)

    if status_indicator not in [
        definitions.PROCESSING_STATUS_COMPLETED,
        definitions.PROCESSING_STATUS_INITIALIZED,
        definitions.PROCESSING_STATUS_RUNNING,
        definitions.PROCESSING_STATUS_PARSING,
        definitions.PROCESSING_STATUS_HASHING]:

      logging.error(
          (u'Process {0:s} (PID: {1:d}) is not functioning correctly. '
           u'Status code {2!s}.').format(
               process.name, pid, status_indicator))

      self._processing_status.error_detected = True

      if process.type == definitions.PROCESS_TYPE_COLLECTOR:
        raise errors.EngineAbort(u'Collector unexpectedly terminated')

      if process.type == definitions.PROCESS_TYPE_STORAGE_WRITER:
        raise errors.EngineAbort(u'Storage writer unexpectedly terminated')

      self._TerminateProcess(pid)

      logging.info(u'Starting replacement worker process for {0:s}'.format(
          process.name))
      worker_process = self._StartExtractionWorkerProcess()
      self._StartMonitoringProcess(worker_process.pid)

    elif status_indicator == definitions.PROCESSING_STATUS_COMPLETED:
      if process.type == definitions.PROCESS_TYPE_WORKER:
        number_of_events = process_status.get(u'number_of_events', 0)
        number_of_pathspecs = process_status.get(
            u'consumed_number_of_path_specs', 0)
        logging.debug((
            u'Process {0:s} (PID: {1:d}) has completed its processing. '
            u'Total of {2:d} events extracted from {3:d} pathspecs').format(
                process.name, pid, number_of_events, number_of_pathspecs))
      elif process.type == definitions.PROCESS_TYPE_COLLECTOR:
        number_of_pathspecs = process_status.get(
            u'produced_number_of_path_specs', 0)
        logging.debug((
            u'Process {0:s} (PID: {1:d}) has completed its processing. '
            u'Total of {2:d} pathspecs extracted').format(
                process.name, pid, number_of_pathspecs))
      elif process.type == definitions.PROCESS_TYPE_STORAGE_WRITER:
        logging.debug((
            u'Process {0:s} (PID: {1:d}) has completed its processing. '
            u'Total of {2:d} events written').format(
                process.name, pid, process_status.get(u'number_of_events', 0)))

      self._StopMonitoringProcess(pid)

    elif self._show_memory_usage:
      self._LogMemoryUsage(pid)