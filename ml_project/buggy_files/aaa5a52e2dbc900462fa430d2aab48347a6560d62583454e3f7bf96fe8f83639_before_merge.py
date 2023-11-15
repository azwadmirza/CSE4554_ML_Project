  def __init__(
      self, task_queue, storage_writer, knowledge_base, session_identifier,
      debug_output=False, enable_profiling=False, filter_object=None,
      hasher_names_string=None, mount_path=None, parser_filter_expression=None,
      preferred_year=None, process_archive_files=False,
      profiling_directory=None, profiling_sample_rate=1000,
      profiling_type=u'all', temporary_directory=None, text_prepend=None,
      yara_rules_string=None, **kwargs):
    """Initializes a worker process.

    Non-specified keyword arguments (kwargs) are directly passed to
    multiprocessing.Process.

    Args:
      task_queue (Queue): task queue.
      storage_writer (StorageWriter): storage writer for a session storage.
      knowledge_base (KnowledgeBase): knowledge base which contains
          information from the source data needed for parsing.
      session_identifier (str): identifier of the session.
      debug_output (Optional[bool]): True if debug output should be enabled.
      enable_profiling (Optional[bool]): True if profiling should be enabled.
      filter_object (Optional[objectfilter.Filter]): filter object.
      hasher_names_string (Optional[str]): comma separated string of names
          of hashers to use during processing.
      mount_path (Optional[str]): mount path.
      parser_filter_expression (Optional[str]): parser filter expression,
          where None represents all parsers and plugins.
      preferred_year (Optional[int]): preferred year.
      process_archive_files (Optional[bool]): True if archive files should be
          scanned for file entries.
      profiling_directory (Optional[str]): path to the directory where
          the profiling sample files should be stored.
      profiling_sample_rate (Optional[int]): the profiling sample rate.
          Contains the number of event sources processed.
      profiling_type (Optional[str]): type of profiling.
          Supported types are:

          * 'memory' to profile memory usage;
          * 'parsers' to profile CPU time consumed by individual parsers;
          * 'processing' to profile CPU time consumed by different parts of
            the processing;
          * 'serializers' to profile CPU time consumed by individual
            serializers.
      temporary_directory (Optional[str]): path of the directory for temporary
          files.
      text_prepend (Optional[str]): text to prepend to every event.
      yara_rules_string (Optional[str]): unparsed yara rule definitions.
      kwargs: keyword arguments to pass to multiprocessing.Process.
    """
    super(WorkerProcess, self).__init__(**kwargs)
    self._abort = False
    self._buffer_size = 0
    self._current_display_name = u''
    self._debug_output = debug_output
    self._enable_profiling = enable_profiling
    self._extraction_worker = None
    self._filter_object = filter_object
    self._hasher_names_string = hasher_names_string
    self._knowledge_base = knowledge_base
    self._memory_profiler = None
    self._mount_path = mount_path
    self._number_of_consumed_events = 0
    self._number_of_consumed_sources = 0
    self._parser_filter_expression = parser_filter_expression
    self._parser_mediator = None
    self._parsers_profiler = None
    self._preferred_year = preferred_year
    self._process_archive_files = process_archive_files
    self._processing_profiler = None
    self._profiling_directory = profiling_directory
    self._profiling_sample_rate = profiling_sample_rate
    self._profiling_type = profiling_type
    self._serializers_profiler = None
    self._session_identifier = session_identifier
    self._status = definitions.PROCESSING_STATUS_INITIALIZED
    self._storage_writer = storage_writer
    self._task_identifier = u''
    self._task_queue = task_queue
    self._temporary_directory = temporary_directory
    self._text_prepend = text_prepend
    self._yara_rules_string = yara_rules_string