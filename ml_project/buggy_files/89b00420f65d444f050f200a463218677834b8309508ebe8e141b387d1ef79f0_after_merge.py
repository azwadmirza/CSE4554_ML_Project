  def _ParseContainerTable(
      self, parser_context, file_entry=None, parser_chain=None, table=None,
      container_name=u'Unknown'):
    """Parses a Container_# table.

    Args:
      parser_context: A parser context object (instance of ParserContext).
      file_entry: Optional file entry object (instance of dfvfs.FileEntry).
      parser_chain: Optional string containing the parsing chain up to this
                    point.
      table: Optional table object (instance of pyesedb.table).
      container_name: Optional string that contains the container name.
                      The container name indicates the table type.
                      The default is a string containing 'Unknown'.
    """
    if table is None:
      logging.warning(u'[{0:s}] invalid Container_# table'.format(self.NAME))
      return

    for esedb_record in table.records:
      # TODO: add support for:
      # wpnidm, iecompat, iecompatua, DNTException, DOMStore
      if container_name == u'Content':
        value_mappings = self._CONTAINER_TABLE_VALUE_MAPPINGS
      else:
        value_mappings = None

      try:
        record_values = self._GetRecordValues(
            table.name, esedb_record, value_mappings=value_mappings)
      except UnicodeDecodeError as exception:
        logging.error((
            u'[{0:s}] Unable to return record values for {1:s} with error: '
            u'{2:s}').format(
                parser_chain,
                file_entry.path_spec.comparable.replace(u'\n', u';'),
                exception))
        continue

      if (container_name in [
          u'Content', u'Cookies', u'History', u'iedownload'] or
          container_name.startswith(u'MSHist')):
        timestamp = record_values.get(u'SyncTime', 0)
        if timestamp:
          event_object = MsieWebCacheContainerEventObject(
              timestamp, u'Synchronization time', record_values)
          parser_context.ProduceEvent(
              event_object, parser_chain=parser_chain, file_entry=file_entry)

        timestamp = record_values.get(u'CreationTime', 0)
        if timestamp:
          event_object = MsieWebCacheContainerEventObject(
              timestamp, eventdata.EventTimestamp.CREATION_TIME, record_values)
          parser_context.ProduceEvent(
              event_object, parser_chain=parser_chain, file_entry=file_entry)

        timestamp = record_values.get(u'ExpiryTime', 0)
        if timestamp:
          event_object = MsieWebCacheContainerEventObject(
              timestamp, eventdata.EventTimestamp.EXPIRATION_TIME,
              record_values)
          parser_context.ProduceEvent(
              event_object, parser_chain=parser_chain, file_entry=file_entry)

        timestamp = record_values.get(u'ModifiedTime', 0)
        if timestamp:
          event_object = MsieWebCacheContainerEventObject(
              timestamp, eventdata.EventTimestamp.MODIFICATION_TIME,
              record_values)
          parser_context.ProduceEvent(
              event_object, parser_chain=parser_chain, file_entry=file_entry)

        timestamp = record_values.get(u'AccessedTime', 0)
        if timestamp:
          event_object = MsieWebCacheContainerEventObject(
              timestamp, eventdata.EventTimestamp.ACCESS_TIME, record_values)
          parser_context.ProduceEvent(
              event_object, parser_chain=parser_chain, file_entry=file_entry)

        timestamp = record_values.get(u'PostCheckTime', 0)
        if timestamp:
          event_object = MsieWebCacheContainerEventObject(
              timestamp, u'Post check time', record_values)
          parser_context.ProduceEvent(
              event_object, parser_chain=parser_chain, file_entry=file_entry)