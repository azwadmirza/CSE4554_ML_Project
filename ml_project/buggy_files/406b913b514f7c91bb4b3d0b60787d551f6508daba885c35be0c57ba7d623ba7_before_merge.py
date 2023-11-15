  def __init__(
      self, event_queue, storage_writer, knowledge_base, analysis_plugin,
      data_location=None, event_filter_expression=None, **kwargs):
    """Initializes an analysis process.

    Non-specified keyword arguments (kwargs) are directly passed to
    multiprocessing.Process.

    Args:
      event_queue (plaso_queue.Queue): event queue.
      storage_writer (StorageWriter): storage writer for a session storage.
      knowledge_base (KnowledgeBase): contains information from the source
          data needed for analysis.
      plugin (AnalysisProcess): plugin running in the process.
      data_location (Optional[str]): path to the location that data files
          should be loaded from.
      event_filter_expression (Optional[str]): event filter expression.
    """
    super(AnalysisProcess, self).__init__(**kwargs)
    self._abort = False
    self._analysis_mediator = None
    self._analysis_plugin = analysis_plugin
    self._data_location = data_location
    self._debug_output = False
    self._event_filter_expression = event_filter_expression
    self._event_queue = event_queue
    self._knowledge_base = knowledge_base
    self._memory_profiler = None
    self._number_of_consumed_events = 0
    self._serializers_profiler = None
    self._status = definitions.PROCESSING_STATUS_INITIALIZED
    self._storage_writer = storage_writer
    self._task = None