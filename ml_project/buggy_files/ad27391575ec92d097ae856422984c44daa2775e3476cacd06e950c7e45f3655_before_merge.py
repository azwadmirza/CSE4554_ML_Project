  def _Open(
      self, path, access_mode=u'r',
      serializer_format=definitions.SERIALIZER_FORMAT_PROTOBUF):
    """Opens the storage file.

    Args:
      path: string containing the path of the storage file.
      access_mode: optional string indicating the access mode.
      serializer_format: Optional storage serializer format.

    Raises:
      IOError: if the file is opened in read only mode and the file does
               not exist.
    """
    super(StorageFile, self)._Open(path, access_mode=access_mode)

    serializer_stream_name = u'serializer.txt'
    has_serializer_stream = self._HasStream(serializer_stream_name)
    if has_serializer_stream:
      stored_serializer_format = self._ReadStream(serializer_stream_name)
      if stored_serializer_format:
        serializer_format = stored_serializer_format

    self._SetSerializerFormat(serializer_format)

    if access_mode != u'r' and not has_serializer_stream:
      # Note that _serializer_format_string is set by _SetSerializerFormat().
      self._WriteStream(serializer_stream_name, self._serializer_format_string)

    if not self._read_only:
      logging.debug(u'Writing to ZIP file with buffer size: {0:d}'.format(
          self._max_buffer_size))

      if self._pre_obj:
        self._pre_obj.counter = collections.Counter()
        self._pre_obj.plugin_counter = collections.Counter()

      # Start up a counter for modules in buffer.
      self._count_data_type = collections.Counter()
      self._count_parser = collections.Counter()

      # Need to get the last number in the list.
      for stream_name in self._GetStreamNames():
        if stream_name.startswith(u'plaso_meta.'):
          _, _, file_number = stream_name.partition(u'.')

          try:
            file_number = int(file_number, 10)
            if file_number >= self._file_number:
              self._file_number = file_number + 1
          except ValueError:
            # Ignore invalid metadata stream names.
            pass

      self._first_file_number = self._file_number