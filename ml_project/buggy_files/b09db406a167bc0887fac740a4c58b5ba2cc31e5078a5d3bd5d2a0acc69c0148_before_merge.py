  def CompleteTask(self, task):
    """Completes a task.

    The task is complete and can be removed from the task manager.

    Args:
      task (Task): unique identifier of the task.

    Raises:
      KeyError: if the task was not active.
    """
    if task.identifier not in self._active_tasks:
      raise KeyError(u'Task not active')

    del self._active_tasks[task.identifier]