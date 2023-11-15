  def __init__(self, *args, **kwargs):
    """
    :API: public
    """
    super(RunTracker, self).__init__(*args, **kwargs)
    self._run_timestamp = time.time()
    self._cmd_line = ' '.join(['pants'] + sys.argv[1:])
    self._sorted_goal_infos = tuple()

    # Initialized in `initialize()`.
    self.run_info_dir = None
    self.run_info = None
    self.cumulative_timings = None
    self.self_timings = None
    self.artifact_cache_stats = None
    self.pantsd_stats = None

    # Initialized in `start()`.
    self.report = None
    self._main_root_workunit = None
    self._all_options = None

    # A lock to ensure that adding to stats at the end of a workunit
    # operates thread-safely.
    self._stats_lock = threading.Lock()

    # Log of success/failure/aborted for each workunit.
    self.outcomes = {}

    # Number of threads for foreground work.
    self._num_foreground_workers = self.get_options().num_foreground_workers

    # Number of threads for background work.
    self._num_background_workers = self.get_options().num_background_workers

    # self._threadlocal.current_workunit contains the current workunit for the calling thread.
    # Note that multiple threads may share a name (e.g., all the threads in a pool).
    self._threadlocal = threading.local()

    # A logger facade that logs into this RunTracker.
    self._logger = RunTrackerLogger(self)

    # For background work.  Created lazily if needed.
    self._background_worker_pool = None
    self._background_root_workunit = None

    # Trigger subproc pool init while our memory image is still clean (see SubprocPool docstring).
    SubprocPool.set_num_processes(self._num_foreground_workers)
    SubprocPool.foreground()

    self._aborted = False

    # Data will be organized first by target and then scope.
    # Eg:
    # {
    #   'target/address:name': {
    #     'running_scope': {
    #       'run_duration': 356.09
    #     },
    #     'GLOBAL': {
    #       'target_type': 'pants.test'
    #     }
    #   }
    # }
    self._target_to_data = {}

    self._end_memoized_result = None