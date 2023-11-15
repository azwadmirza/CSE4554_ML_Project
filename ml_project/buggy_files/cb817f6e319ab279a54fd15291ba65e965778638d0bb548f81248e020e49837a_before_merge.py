  def __init__(
      self, output_file, buffer_size=0, read_only=False, pre_obj=None,
      serializer_format=definitions.SERIALIZER_FORMAT_PROTOBUF):
    """Initializes the storage file.

    Args:
      output_file: The name of the output file.
      buffer_size: Optional maximum size of a single storage (protobuf) file.
                   The default is 0, which indicates no limit.
      read_only: Optional boolean to indicate we are opening the storage file
                 for reading only.
      pre_obj: Optional preprocessing object that gets stored inside
               the storage file.
      serializer_format: Optional storage serializer format.

    Raises:
      IOError: if we open up the file in read only mode and the file does
      not exist.
    """
    super(StorageFile, self).__init__()
    self._buffer = []
    self._buffer_first_timestamp = sys.maxint
    self._buffer_last_timestamp = 0
    self._buffer_size = 0
    self._event_object_serializer = None
    self._event_tag_index = None
    self._file_number = 1
    self._first_file_number = None
    self._max_buffer_size = buffer_size or self.MAXIMUM_BUFFER_SIZE
    self._merge_buffer = None
    self._output_file = output_file
    self._pre_obj = pre_obj
    self._read_only = read_only
    self._serializer_format_string = u''
    self._write_counter = 0

    if self._read_only:
      access_mode = u'r'
    else:
      access_mode = u'a'

    self._Open(
        output_file, access_mode=access_mode,
        serializer_format=serializer_format)

    # Attributes for profiling.
    self._enable_profiling = False
    self._profiling_sample = 0
    self._serializers_profiler = None