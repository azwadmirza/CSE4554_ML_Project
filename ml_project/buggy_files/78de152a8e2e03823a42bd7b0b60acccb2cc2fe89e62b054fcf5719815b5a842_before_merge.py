  def __init__(self, zip_file, stream_name, access_mode='r'):
    """Initializes a serialized data offset table object.

    Args:
      zip_file: the ZIP file object that contains the stream.
      stream_name: string containing the name of the stream.
      access_mode: optional string containing the access mode.
                   The default is read-only ('r').
    """
    super(_SerializedDataOffsetTable, self).__init__()
    self._access_mode = access_mode
    self._offsets = []
    self._stream_name = stream_name
    self._zip_file = zip_file