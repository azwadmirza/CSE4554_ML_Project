  def RescheduleTaskByIdentifier(self, task_identifier):
    """Reschedules a previous abandoned task.

    Args:
      task_identifier (str): unique identifier of the task.

    Raises:
      KeyError: if the task was not abandoned.
    """
    if task_identifier not in self._abandoned_tasks:
      raise KeyError(u'Task not abandoned')

    task = self._abandoned_tasks[task_identifier]
    self._active_tasks[task_identifier] = task
    del self._abandoned_tasks[task_identifier]

    task.UpdateProcessingTime()
    self._tasks_processing[task_identifier] = task