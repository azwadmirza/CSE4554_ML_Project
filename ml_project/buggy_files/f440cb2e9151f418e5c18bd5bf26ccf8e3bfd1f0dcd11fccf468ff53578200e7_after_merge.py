  def _PrintStatusUpdateStream(self, processing_status):
    """Prints the processing status as a stream of output.

    Args:
      processing_status: the processing status (instance of ProcessingStatus).
    """
    if processing_status.GetExtractionCompleted():
      self._output_writer.Write(
          u'All extraction workers completed - waiting for storage.\n')

    else:
      for extraction_worker_status in processing_status.extraction_workers:
        status = extraction_worker_status.status
        self._output_writer.Write((
            u'{0:s} (PID: {1:d}) - events extracted: {2:d} - file: {3:s} '
            u'- running: {4!s} <{5:s}>\n').format(
                extraction_worker_status.identifier,
                extraction_worker_status.pid,
                extraction_worker_status.number_of_events,
                extraction_worker_status.display_name,
                status in [definitions.PROCESSING_STATUS_RUNNING,
                           definitions.PROCESSING_STATUS_HASHING,
                           definitions.PROCESSING_STATUS_PARSING],
                extraction_worker_status.process_status))