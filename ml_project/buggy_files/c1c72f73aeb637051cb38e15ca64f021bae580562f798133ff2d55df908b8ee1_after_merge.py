  def _StartExtractionWorkerProcess(self, storage_writer):
    """Creates, starts and registers an extraction worker process.

    Args:
      storage_writer (StorageWriter): storage writer for a session storage used
          to create task storage.

    Returns:
      MultiProcessWorkerProcess: extraction worker process.
    """
    process_name = u'Worker_{0:02d}'.format(self._last_worker_number)
    logging.debug(u'Starting worker process {0:s}'.format(process_name))

    if self._use_zeromq:
      task_queue = zeromq_queue.ZeroMQRequestConnectQueue(
          delay_open=True, name=u'{0:s} task queue'.format(process_name),
          linger_seconds=0, port=self._task_queue_port,
          timeout_seconds=2)
    else:
      task_queue = self._task_queue

    process = worker_process.WorkerProcess(
        task_queue, storage_writer, self.knowledge_base,
        self._session_identifier, debug_output=self._debug_output,
        enable_profiling=self._enable_profiling,
        enable_sigsegv_handler=self._enable_sigsegv_handler,
        filter_object=self._filter_object,
        hasher_names_string=self._hasher_names_string,
        mount_path=self._mount_path, name=process_name,
        parser_filter_expression=self._parser_filter_expression,
        preferred_year=self._preferred_year,
        process_archive_files=self._process_archive_files,
        profiling_directory=self._profiling_directory,
        profiling_sample_rate=self._profiling_sample_rate,
        profiling_type=self._profiling_type,
        temporary_directory=self._temporary_directory,
        text_prepend=self._text_prepend,
        yara_rules_string=self._yara_rules_string)

    process.start()
    self._last_worker_number += 1

    self._RegisterProcess(process)

    return process