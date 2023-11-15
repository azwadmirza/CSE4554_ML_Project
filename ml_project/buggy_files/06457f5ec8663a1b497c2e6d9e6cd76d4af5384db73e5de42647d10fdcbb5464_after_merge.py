  def _ParseUrl(
      self, parser_mediator, format_version, cache_directories, msiecf_item,
      recovered=False):
    """Extract data from a MSIE Cache Files (MSIECF) URL item.

       Every item is stored as an event object, one for each timestamp.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      format_version: The MSIECF format version.
      cache_directories: A list of cache directory names.
      msiecf_item: An item (pymsiecf.url).
      recovered: Boolean value to indicate the item was recovered, False
                 by default.
    """
    # The secondary timestamp can be stored in either UTC or local time
    # this is dependent on what the index.dat file is used for.
    # Either the file path or location string can be used to distinguish
    # between the different type of files.
    primary_timestamp = timelib.Timestamp.FromFiletime(
        msiecf_item.get_primary_time_as_integer())
    primary_timestamp_description = u'Primary Time'

    # Need to convert the FILETIME to the internal timestamp here to
    # do the from localtime conversion.
    secondary_timestamp = timelib.Timestamp.FromFiletime(
        msiecf_item.get_secondary_time_as_integer())
    secondary_timestamp_description = u'Secondary Time'

    if msiecf_item.type:
      if msiecf_item.type == u'cache':
        primary_timestamp_description = eventdata.EventTimestamp.ACCESS_TIME
        secondary_timestamp_description = (
            eventdata.EventTimestamp.MODIFICATION_TIME)

      elif msiecf_item.type == u'cookie':
        primary_timestamp_description = eventdata.EventTimestamp.ACCESS_TIME
        secondary_timestamp_description = (
            eventdata.EventTimestamp.MODIFICATION_TIME)

      elif msiecf_item.type == u'history':
        primary_timestamp_description = (
            eventdata.EventTimestamp.LAST_VISITED_TIME)
        secondary_timestamp_description = (
            eventdata.EventTimestamp.LAST_VISITED_TIME)

      elif msiecf_item.type == u'history-daily':
        primary_timestamp_description = (
            eventdata.EventTimestamp.LAST_VISITED_TIME)
        secondary_timestamp_description = (
            eventdata.EventTimestamp.LAST_VISITED_TIME)
        # The secondary_timestamp is in localtime normalize it to be in UTC.
        secondary_timestamp = timelib.Timestamp.LocaltimeToUTC(
            secondary_timestamp, parser_mediator.timezone)

      elif msiecf_item.type == u'history-weekly':
        primary_timestamp_description = eventdata.EventTimestamp.CREATION_TIME
        secondary_timestamp_description = (
            eventdata.EventTimestamp.LAST_VISITED_TIME)
        # The secondary_timestamp is in localtime normalize it to be in UTC.
        secondary_timestamp = timelib.Timestamp.LocaltimeToUTC(
            secondary_timestamp, parser_mediator.timezone)

    http_headers = u''
    if msiecf_item.type and msiecf_item.data:
      if msiecf_item.type == u'cache':
        if msiecf_item.data[:4] == b'HTTP':
          # Make sure the HTTP headers are ASCII encoded.
          # TODO: determine correct encoding currently indications that
          # this could be the system narrow string codepage.
          try:
            http_headers = msiecf_item.data[:-1].decode(u'ascii')
          except UnicodeDecodeError:
            parser_mediator.ProduceParseError((
                u'unable to decode HTTP headers of URL record at offset: '
                u'0x{0:08x}. Characters that cannot be decoded will be '
                u'replaced with "?" or "\\ufffd".').format(msiecf_item.offset))
            http_headers = msiecf_item.data[:-1].decode(
                u'ascii', errors=u'replace')

      # TODO: parse data of other URL item type like history which requires
      # OLE VT parsing.

    event_object = MsiecfUrlEvent(
        primary_timestamp, primary_timestamp_description, cache_directories,
        msiecf_item, http_headers=http_headers, recovered=recovered)
    parser_mediator.ProduceEvent(event_object)

    if secondary_timestamp > 0:
      event_object = MsiecfUrlEvent(
          secondary_timestamp, secondary_timestamp_description,
          cache_directories, msiecf_item, http_headers=http_headers,
          recovered=recovered)
      parser_mediator.ProduceEvent(event_object)

    expiration_timestamp = msiecf_item.get_expiration_time_as_integer()
    if expiration_timestamp > 0:
      # The expiration time in MSIECF version 4.7 is stored as a FILETIME value
      # in version 5.2 it is stored as a FAT date time value.
      # Since the as_integer function returns the raw integer value we need to
      # apply the right conversion here.
      if format_version == u'4.7':
        event_object = MsiecfUrlEvent(
            timelib.Timestamp.FromFiletime(expiration_timestamp),
            eventdata.EventTimestamp.EXPIRATION_TIME, cache_directories,
            msiecf_item, http_headers=http_headers, recovered=recovered)
      else:
        event_object = MsiecfUrlEvent(
            timelib.Timestamp.FromFatDateTime(expiration_timestamp),
            eventdata.EventTimestamp.EXPIRATION_TIME, cache_directories,
            msiecf_item, http_headers=http_headers, recovered=recovered)

      parser_mediator.ProduceEvent(event_object)

    last_checked_timestamp = msiecf_item.get_last_checked_time_as_integer()
    if last_checked_timestamp > 0:
      event_object = MsiecfUrlEvent(
          timelib.Timestamp.FromFatDateTime(last_checked_timestamp),
          eventdata.EventTimestamp.LAST_CHECKED_TIME, cache_directories,
          msiecf_item, http_headers=http_headers, recovered=recovered)
      parser_mediator.ProduceEvent(event_object)