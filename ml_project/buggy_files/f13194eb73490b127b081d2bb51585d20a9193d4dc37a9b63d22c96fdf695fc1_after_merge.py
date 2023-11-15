  def __init__(self, maximum_number_of_tasks=0):
    """Initializes a task manager object.

    Args:
      maximum_number_of_tasks (Optional[int]): maximum number of concurrent
          tasks, where 0 represents no limit.
    """
    super(TaskManager, self).__init__()
    # Dictionary mapping task identifiers to tasks which have been abandoned.
    self._abandoned_tasks = {}
    # Dictionary mapping task identifiers to tasks that are active.
    self._active_tasks = {}
    self._lock = threading.Lock()
    self._maximum_number_of_tasks = maximum_number_of_tasks
    self._tasks_pending_merge = _PendingMergeTaskHeap()
    # Use ordered dictionaries to preserve the order in which tasks were added.
    # This dictionary maps task identifiers to tasks.
    self._tasks_processing = collections.OrderedDict()