  def GetAbandonedTasks(self):
    """Retrieves all abandoned tasks.

    Returns:
      list[Task]: tasks.
    """
    with self._lock:
      abandoned_tasks = list(self._abandoned_tasks.values())
    return abandoned_tasks