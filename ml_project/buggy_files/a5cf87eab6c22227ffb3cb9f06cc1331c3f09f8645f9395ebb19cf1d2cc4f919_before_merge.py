  def __init__(
      self, session, storage_type=definitions.STORAGE_TYPE_SESSION, task=None):
    """Initializes a storage writer.

    Args:
      session (Session): session the storage changes are part of.
      storage_type (Optional[str]): storage type.
      task(Optional[Task]): task.
    """
    super(StorageWriter, self).__init__()
    self._first_written_event_source_index = 0
    self._session = session
    self._storage_type = storage_type
    self._task = task
    self._written_event_source_index = 0
    self.number_of_errors = 0
    self.number_of_event_sources = 0
    self.number_of_events = 0