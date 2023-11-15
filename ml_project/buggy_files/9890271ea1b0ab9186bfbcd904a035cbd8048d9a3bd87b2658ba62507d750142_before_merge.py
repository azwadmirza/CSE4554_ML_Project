  def __init__(self, storage_writer, path):
    """Initializes a storage merge reader.

    Args:
      storage_writer (StorageWriter): storage writer.
      path (str): path to the input file.
    """
    super(GZIPStorageMergeReader, self).__init__(storage_writer)
    self._data_buffer = None
    self._gzip_file = gzip.open(path, 'rb')
    self._path = path
    self._serializer = json_serializer.JSONAttributeContainerSerializer
    self._serializers_profiler = None