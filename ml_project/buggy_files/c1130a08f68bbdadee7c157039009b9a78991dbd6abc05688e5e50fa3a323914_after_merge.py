  def HasActiveTasks(self):
    """Determines if there are active tasks.

    A task is considered abandoned if its last update exceeds the inactive time.

    Returns:
      bool: True if there are active tasks.
    """
    with self._lock:
      if not self._active_tasks:
        return False

      inactive_time = int(time.time() * 1000000) - self._TASK_INACTIVE_TIME

      for task in iter(self._tasks_processing.values()):
        # Use a local variable to improve performance.
        task_identifier = task.identifier
        if task.last_processing_time < inactive_time:
          del self._tasks_processing[task_identifier]
          self._abandoned_tasks[task_identifier] = task
          del self._active_tasks[task_identifier]

      return bool(self._active_tasks)