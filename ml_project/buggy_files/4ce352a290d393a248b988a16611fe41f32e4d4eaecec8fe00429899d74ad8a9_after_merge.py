  def _UpdateStatus(
      self, status, display_name, number_of_consumed_sources, storage_writer,
      force=False):
    """Updates the processing status.

    Args:
      status (str): human readable status of the processing e.g. 'Idle'.
      display_name (str): human readable of the file entry currently being
          processed.
      number_of_consumed_sources (int): number of consumed sources.
      storage_writer (StorageWriter): storage writer for a session storage.
      force (Optional[bool]): True if the update should be forced ignoring
          the last status update time.
    """
    current_timestamp = time.time()
    if not force and current_timestamp < (
        self._last_status_update_timestamp + self._STATUS_UPDATE_INTERVAL):
      return

    if status == definitions.PROCESSING_STATUS_IDLE:
      status = definitions.PROCESSING_STATUS_RUNNING

    self._processing_status.UpdateForemanStatus(
        self._name, status, self._pid, display_name,
        number_of_consumed_sources, storage_writer.number_of_event_sources,
        0, storage_writer.number_of_events,
        0, 0,
        0, storage_writer.number_of_errors,
        0, 0)

    if self._status_update_callback:
      self._status_update_callback(self._processing_status)

    self._last_status_update_timestamp = current_timestamp