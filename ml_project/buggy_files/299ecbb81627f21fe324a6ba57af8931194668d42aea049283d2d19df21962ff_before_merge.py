  def GetProcessingTasks(self):
    """Retrieves the tasks that are processing.

    Returns:
      list[Task]: tasks that are being processed by workers.
    """
    return list(self._tasks_processing.values())