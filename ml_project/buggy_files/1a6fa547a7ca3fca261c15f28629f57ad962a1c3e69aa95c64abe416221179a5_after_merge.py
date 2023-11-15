  def UpdateTaskAsProcessing(self, task):
    """Updates the task manager to reflect the task is processing.

    Args:
      task (Task): task.

    Raises:
      KeyError: if the task is already processing.
    """
    if task.identifier in self._tasks_processing:
      raise KeyError(u'Task already processing')

    with self._lock:
      # TODO: add check for maximum_number_of_tasks.
      task.UpdateProcessingTime()
      self._tasks_processing[task.identifier] = task