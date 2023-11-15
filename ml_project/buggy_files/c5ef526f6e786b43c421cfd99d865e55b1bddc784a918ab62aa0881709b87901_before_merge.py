  def UpdateTaskAsPendingMerge(self, task):
    """Updates the task manager to reflect the task is ready to be merged.

    Args:
      task (Task): task.

    Raises:
      KeyError: if the task was not processing.
    """
    if task.identifier not in self._tasks_processing:
      raise KeyError(u'Task not processing')

    self._tasks_pending_merge.PushTask(task)
    del self._tasks_processing[task.identifier]