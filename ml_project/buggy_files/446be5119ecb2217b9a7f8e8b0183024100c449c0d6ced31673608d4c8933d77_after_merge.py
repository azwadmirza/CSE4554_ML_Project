  def __init__(self):
    """Initializes a ZIP-based storage file object."""
    super(ZIPStorageFile, self).__init__()
    self._event_object_streams = {}
    self._offset_tables = {}
    self._offset_tables_lfu = []
    self._path = None
    self._timestamp_tables = {}
    self._timestamp_tables_lfu = []
    self._zipfile = None