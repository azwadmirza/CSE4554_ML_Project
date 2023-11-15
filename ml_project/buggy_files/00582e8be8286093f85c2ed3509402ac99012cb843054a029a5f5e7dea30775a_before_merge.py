  def _WriteBuffer(self):
    """Writes the buffered event objects to the storage file."""
    if not self._buffer_size:
      return

    stream_name = u'plaso_index.{0:06d}'.format(self._file_number)
    offset_table = _SerializedDataOffsetTable(self._zipfile, stream_name)

    stream_name = u'plaso_timestamps.{0:06d}'.format(self._file_number)
    timestamp_table = _SerializedDataTimestampTable(self._zipfile, stream_name)

    if self._serializers_profiler:
      self._serializers_profiler.StartTiming(u'write')

    stream_name = u'plaso_proto.{0:06d}'.format(self._file_number)
    data_stream = _SerializedDataStream(self._zipfile, stream_name)
    entry_data_offset = data_stream.WriteInitialize()
    try:
      for _ in range(len(self._buffer)):
        timestamp, entry_data = heapq.heappop(self._buffer)

        timestamp_table.AddTimestamp(timestamp)
        offset_table.AddOffset(entry_data_offset)

        entry_data_offset = data_stream.WriteEntry(entry_data)

    except:
      data_stream.WriteAbort()

      if self._serializers_profiler:
        self._serializers_profiler.StopTiming(u'write')

      raise

    self._WriteMetadata(
        self._file_number, self._buffer_first_timestamp,
        self._buffer_last_timestamp)

    offset_table.Write()
    data_stream.WriteFinalize()
    timestamp_table.Write()

    if self._serializers_profiler:
      self._serializers_profiler.StopTiming(u'write')

    # Reset the counters.
    self._count_data_type = collections.Counter()
    self._count_parser = collections.Counter()

    self._file_number += 1
    self._buffer_size = 0
    self._buffer = []
    self._buffer_first_timestamp = sys.maxint
    self._buffer_last_timestamp = -sys.maxint - 1