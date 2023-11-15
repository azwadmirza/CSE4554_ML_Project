  def __init__(
      self, debug_output=False, enable_profiling=False,
      maximum_number_of_tasks=_MAXIMUM_NUMBER_OF_TASKS,
      profiling_directory=None, profiling_sample_rate=1000,
      profiling_type=u'all', use_zeromq=True):
    """Initializes an engine object.

    Args:
      debug_output (Optional[bool]): True if debug output should be enabled.
      enable_profiling (Optional[bool]): True if profiling should be enabled.
      maximum_number_of_tasks (Optional[int]): maximum number of concurrent
          tasks, where 0 represents no limit.
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
      use_zeromq (Optional[bool]): True if ZeroMQ should be used for queuing
          instead of Python's multiprocessing queue.
    """
    super(TaskMultiProcessEngine, self).__init__(
        debug_output=debug_output, enable_profiling=enable_profiling,
        profiling_directory=profiling_directory,
        profiling_sample_rate=profiling_sample_rate,
        profiling_type=profiling_type)
    self._enable_sigsegv_handler = False
    self._filter_find_specs = None
    self._filter_object = None
    self._hasher_names_string = None
    self._last_worker_number = 0
    self._maximum_number_of_tasks = maximum_number_of_tasks
    self._memory_profiler = None
    self._merge_task = None
    self._merge_task_on_hold = None
    self._mount_path = None
    self._number_of_consumed_errors = 0
    self._number_of_consumed_events = 0
    self._number_of_consumed_reports = 0
    self._number_of_consumed_sources = 0
    self._number_of_produced_errors = 0
    self._number_of_produced_events = 0
    self._number_of_produced_reports = 0
    self._number_of_produced_sources = 0
    self._number_of_worker_processes = 0
    self._parser_filter_expression = None
    self._preferred_year = None
    self._process_archive_files = False
    self._processing_profiler = None
    self._resolver_context = context.Context()
    self._serializers_profiler = None
    self._session_identifier = None
    self._status = definitions.PROCESSING_STATUS_IDLE
    self._storage_merge_reader = None
    self._storage_merge_reader_on_hold = None
    self._storage_writer = None
    self._task_queue = None
    self._task_queue_port = None
    self._task_manager = task_manager.TaskManager(
        maximum_number_of_tasks=maximum_number_of_tasks)
    self._temporary_directory = None
    self._text_prepend = None
    self._use_zeromq = use_zeromq
    self._yara_rules_string = None