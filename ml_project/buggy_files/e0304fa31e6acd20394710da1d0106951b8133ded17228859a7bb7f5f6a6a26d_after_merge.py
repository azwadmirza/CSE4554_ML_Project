  def __init__(
      self, timestamp, timestamp_description, cache_directories, msiecf_item,
      http_headers=u'', recovered=False):
    """Initializes the event.

    Args:
      timestamp: the timestamp which is an integer containing the number
                 of micro seconds since January 1, 1970, 00:00:00 UTC.
      timestamp_description: the usage string for the timestamp value.
      cache_directories: a list of cache directory names.
      msiecf_item: the MSIECF item (pymsiecf.url).
      http_headers: a string containing the HTTP headers.
      recovered: a boolean value to indicate the item was recovered.
    """
    super(MsiecfUrlEvent, self).__init__(timestamp, timestamp_description)

    self.cache_directory_index = msiecf_item.cache_directory_index
    self.cached_filename = msiecf_item.filename
    self.cached_file_size = msiecf_item.cached_file_size
    self.http_headers = http_headers
    self.number_of_hits = msiecf_item.number_of_hits
    self.offset = msiecf_item.offset
    self.recovered = recovered
    self.url = msiecf_item.location

    if (msiecf_item.cache_directory_index >= 0 and
        msiecf_item.cache_directory_index < len(cache_directories)):
      self.cache_directory_name = (
          cache_directories[msiecf_item.cache_directory_index])