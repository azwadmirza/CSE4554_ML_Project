  def _GetSerializedDataOffsetTable(
      self, offset_tables_cache, offset_tables_lfu, stream_name_prefix,
      stream_number):
    """Retrieves the serialized data offset table.

    Args:
      offset_tables_cache (dict): offset tables cache.
      offset_tables_lfu (list[_SerializedDataOffsetTable]): least frequently
          used (LFU) offset tables.
      stream_name_prefix (str): stream name prefix.
      stream_number (str): number of the stream.

    Returns:
      _SerializedDataOffsetTable: serialized data offset table.

    Raises:
      IOError: if the stream cannot be opened.
    """
    offset_table = offset_tables_cache.get(stream_number, None)
    if not offset_table:
      stream_name = u'{0:s}.{1:06d}'.format(stream_name_prefix, stream_number)
      if not self._HasStream(stream_name):
        raise IOError(u'No such stream: {0:s}'.format(stream_name))

      offset_table = _SerializedDataOffsetTable(self._zipfile, stream_name)
      offset_table.Read()

      number_of_tables = len(offset_tables_cache)
      if number_of_tables >= self._MAXIMUM_NUMBER_OF_CACHED_TABLES:
        lfu_stream_number = self._event_offset_tables_lfu.pop()
        del offset_tables_cache[lfu_stream_number]

      offset_tables_cache[stream_number] = offset_table

    if stream_number in offset_tables_lfu:
      lfu_index = offset_tables_lfu.index(stream_number)
      offset_tables_lfu.pop(lfu_index)

    offset_tables_lfu.append(stream_number)

    return offset_table