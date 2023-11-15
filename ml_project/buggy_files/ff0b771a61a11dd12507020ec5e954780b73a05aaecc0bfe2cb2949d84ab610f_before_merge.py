  def AnalyzeEvents(
      self, knowledge_base_object, storage_writer, data_location,
      analysis_plugins, event_filter=None, event_filter_expression=None,
      status_update_callback=None):
    """Analyzes events in a plaso storage.

    Args:
      knowledge_base_object (KnowledgeBase): contains information from
          the source data needed for processing.
      storage_writer (StorageWriter): storage writer.
      data_location (str): path to the location that data files should
          be loaded from.
      analysis_plugins (list[AnalysisPlugin]): analysis plugins that should
          be run.
      event_filter (Optional[FilterObject]): event filter.
      event_filter_expression (Optional[str]): event filter expression.
      status_update_callback (Optional[function]): callback function for status
          updates.
    """
    if not analysis_plugins:
      return

    self._status_update_callback = status_update_callback

    # Set up the storage writer before the analysis processes.
    storage_writer.StartTaskStorage()

    self._StartAnalysisProcesses(
        knowledge_base_object, storage_writer, analysis_plugins,
        data_location, event_filter_expression=event_filter_expression)

    # Start the status update thread after open of the storage writer
    # so we don't have to clean up the thread if the open fails.
    self._StartStatusUpdateThread()

    try:
      # Open the storage file after creating the worker processes otherwise
      # the ZIP storage file will remain locked as long as the worker processes
      # are alive.
      storage_writer.Open()
      storage_writer.ReadPreprocessingInformation(knowledge_base_object)
      storage_writer.WriteSessionStart()

      try:
        self._AnalyzeEvents(
            storage_writer, analysis_plugins, event_filter=event_filter)

      except KeyboardInterrupt:
        self._abort = True

        self._processing_status.aborted = True
        if self._status_update_callback:
          self._status_update_callback(self._processing_status)

      finally:
        storage_writer.WriteSessionCompletion(aborted=self._abort)

        storage_writer.Close()

    finally:
      # Stop the status update thread after close of the storage writer
      # so we include the storage sync to disk in the status updates.
      self._StopStatusUpdateThread()

    try:
      self._StopAnalysisProcesses(abort=self._abort)

    except KeyboardInterrupt:
      self._AbortKill()

      # The abort can leave the main process unresponsive
      # due to incorrectly finalized IPC.
      self._KillProcess(os.getpid())

    # Reset values.
    self._status_update_callback = None