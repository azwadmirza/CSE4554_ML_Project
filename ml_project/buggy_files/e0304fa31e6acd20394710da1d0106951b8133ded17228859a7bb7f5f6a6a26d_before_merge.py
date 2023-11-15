  def __init__(
      self, timestamp, timestamp_description, cache_directories, msiecf_item,
      recovered=False):
    """Initializes the event.

    Args:
      timestamp: The timestamp value.
      timestamp_description: The usage string describing the timestamp.
      cache_directories: A list of cache directory names.
      msiecf_item: The MSIECF item (pymsiecf.url).
      recovered: Boolean value to indicate the item was recovered, False
                 by default.
    """
    super(MsiecfUrlEvent, self).__init__(timestamp, timestamp_description)

    self.recovered = recovered
    self.offset = msiecf_item.offset

    self.url = msiecf_item.location
    self.number_of_hits = msiecf_item.number_of_hits
    self.cached_filename = msiecf_item.filename
    self.cached_file_size = msiecf_item.cached_file_size

    self.cache_directory_index = msiecf_item.cache_directory_index
    if (msiecf_item.cache_directory_index >= 0 and
        msiecf_item.cache_directory_index < len(cache_directories)):
      self.cache_directory_name = (
          cache_directories[msiecf_item.cache_directory_index])

    if msiecf_item.type and msiecf_item.data:
      if msiecf_item.type == u'cache':
        if msiecf_item.data[:4] == b'HTTP':
          self.http_headers = msiecf_item.data[:-1]