  def GetProcessingTasks(self):
    """Retrieves the tasks that are processing.

    Returns:
      list[Task]: tasks that are being processed by workers.
    """
    with self._lock:
      processing_tasks = list(self._tasks_processing.values())
    return processing_tasks