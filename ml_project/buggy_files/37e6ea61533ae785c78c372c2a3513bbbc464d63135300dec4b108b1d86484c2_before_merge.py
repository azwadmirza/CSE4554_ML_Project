  def UpdateTaskByIdentifier(self, task_identifier):
    """Updates a task.

    Args:
      task_identifier (str): unique identifier of the task.

    Raises:
      KeyError: if the task is not processing.
    """
    if task_identifier not in self._tasks_processing:
      raise KeyError(u'Task not processing')

    task = self._tasks_processing[task_identifier]
    task.UpdateProcessingTime()