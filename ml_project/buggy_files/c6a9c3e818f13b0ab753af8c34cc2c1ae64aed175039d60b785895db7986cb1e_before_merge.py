  def GetAbandonedTasks(self):
    """Retrieves all abandoned tasks.

    Returns:
      list[task]: task.
    """
    return self._abandoned_tasks.values()