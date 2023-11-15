  def ReportingComplete(self):
    """Called by an analysis plugin to signal that it has generated its report.

    This method signals to report consumers that no further reports will be
    produced by the analysis plugin.
    """
    if self._completion_event:
      self._completion_event.set()
    self._analysis_report_queue_producer.Close()