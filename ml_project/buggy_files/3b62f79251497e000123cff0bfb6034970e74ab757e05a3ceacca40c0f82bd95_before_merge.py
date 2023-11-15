  def GetEntries(self, parser_mediator, registry_key, **kwargs):
    """Extracts event objects from a Application Compatibility Cache key.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      registry_key: A Windows Registry key (instance of
                    dfwinreg.WinRegistryKey).
    """
    value = registry_key.GetValueByName(u'AppCompatCache')
    if not value:
      return

    value_data = value.data
    value_data_size = len(value.data)

    format_type = self._CheckSignature(value_data)
    if not format_type:
      parser_mediator.ProduceParseError(
          u'Unsupported signature in AppCompatCache key: {0:s}'.format(
              registry_key.path))
      return

    header_object = self._ParseHeader(format_type, value_data)

    # On Windows Vista and 2008 when the cache is empty it will
    # only consist of the header.
    if value_data_size <= header_object.header_size:
      return

    cached_entry_offset = header_object.header_size
    cached_entry_size = self._DetermineCacheEntrySize(
        format_type, value_data, cached_entry_offset)

    if not cached_entry_size:
      parser_mediator.ProduceParseError(
          u'Unsupported cached entry size at offset {0:d} in AppCompatCache '
          u'key: {1:s}'.format(cached_entry_offset, registry_key.path))
      return

    cached_entry_index = 0
    while cached_entry_offset < value_data_size:
      cached_entry_object = self._ParseCachedEntry(
          format_type, value_data, cached_entry_offset, cached_entry_size)

      if cached_entry_object.last_modification_time is not None:
        # TODO: refactor to file modification event.
        event_object = AppCompatCacheEvent(
            cached_entry_object.last_modification_time,
            u'File Last Modification Time', registry_key.path,
            cached_entry_index + 1, cached_entry_object.path,
            cached_entry_offset)
        parser_mediator.ProduceEvent(event_object)

      if cached_entry_object.last_update_time is not None:
        # TODO: refactor to process run event.
        event_object = AppCompatCacheEvent(
            cached_entry_object.last_update_time,
            eventdata.EventTimestamp.LAST_RUNTIME, registry_key.path,
            cached_entry_index + 1, cached_entry_object.path,
            cached_entry_offset)
        parser_mediator.ProduceEvent(event_object)

      cached_entry_offset += cached_entry_object.cached_entry_size
      cached_entry_index += 1

      if (header_object.number_of_cached_entries != 0 and
          cached_entry_index >= header_object.number_of_cached_entries):
        break