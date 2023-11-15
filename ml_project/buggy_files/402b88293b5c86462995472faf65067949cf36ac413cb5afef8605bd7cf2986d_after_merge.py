  def PrepareMergeTaskStorage(self, task_name):
    """Prepares a task storage for merging.

    Args:
      task_name (str): unique name of the task.

    Raises:
      IOError: if the storage type is not supported or
               if the temporary path for the task storage does not exist.
    """
    if self._storage_type != definitions.STORAGE_TYPE_SESSION:
      raise IOError(u'Unsupported storage type.')

    if not self._task_storage_path:
      raise IOError(u'Missing task storage path.')

    storage_file_path = os.path.join(
        self._task_storage_path, u'{0:s}.plaso'.format(task_name))

    merge_storage_file_path = os.path.join(
        self._merge_task_storage_path, u'{0:s}.plaso'.format(task_name))

    try:
      os.rename(storage_file_path, merge_storage_file_path)
    except OSError as exception:
      raise IOError((
          u'Unable to rename task storage file: {0:s} with error: '
          u'{1:s}').format(storage_file_path, exception))