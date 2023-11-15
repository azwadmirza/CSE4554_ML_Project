  def ParseFileObject(self, parser_mediator, file_object, **kwargs):
    """Parses a CUPS IPP file-like object.

    Args:
      parser_mediator (ParserMediator): mediates interactions between parsers
          and other components, such as storage and dfvfs.
      file_object (dfvfs.FileIO): file-like object.

    Raises:
      UnableToParseFile: when the file cannot be parsed.
    """
    try:
      header = self.CUPS_IPP_HEADER.parse_stream(file_object)
    except (IOError, construct.FieldError) as exception:
      raise errors.UnableToParseFile(
          u'Unable to parse CUPS IPP Header with error: {0:s}'.format(
              exception))

    if (header.major_version != self.IPP_MAJOR_VERSION or
        header.minor_version != self.IPP_MINOR_VERSION):
      raise errors.UnableToParseFile(
          u'[{0:s}] Unsupported version number.'.format(self.NAME))

    if header.operation_id != self.IPP_OP_ID:
      # Warn if the operation ID differs from the standard one. We should be
      # able to parse the file nonetheless.
      logging.debug(
          u'[{0:s}] Unsupported operation identifier in file: {1:s}.'.format(
              self.NAME, parser_mediator.GetDisplayName()))

    # Read the pairs extracting the name and the value.
    data_dict = {}
    name, value = self._ReadPair(parser_mediator, file_object)
    while name or value:
      # Translate the known "name" CUPS IPP to a generic name value.
      pretty_name = self.NAME_PAIR_TRANSLATION.get(name, name)
      data_dict.setdefault(pretty_name, []).append(value)
      name, value = self._ReadPair(parser_mediator, file_object)

    # TODO: Refactor to use a lookup table to do event production.
    time_dict = {}
    for key, value in data_dict.items():
      if key.startswith(u'date-time-') or key.startswith(u'time-'):
        time_dict[key] = value
        del data_dict[key]

    # TODO: Find a better solution than to have join for each attribute.
    event_data = CupsIppEventData()
    event_data.application = self._ListToString(data_dict.get(
        u'application', None))
    event_data.computer_name = self._ListToString(data_dict.get(
        u'computer_name', None))
    event_data.copies = data_dict.get(u'copies', 0)[0]
    event_data.data_dict = data_dict
    event_data.doc_type = self._ListToString(data_dict.get(u'doc_type', None))
    event_data.job_id = self._ListToString(data_dict.get(u'job_id', None))
    event_data.job_name = self._ListToString(data_dict.get(u'job_name', None))
    event_data.user = self._ListToString(data_dict.get(u'user', None))
    event_data.owner = self._ListToString(data_dict.get(u'owner', None))
    event_data.printer_id = self._ListToString(data_dict.get(
        u'printer_id', None))
    event_data.uri = self._ListToString(data_dict.get(u'uri', None))

    time_value = time_dict.get(u'date-time-at-creation', None)
    if time_value is not None:
      date_time = dfdatetime_posix_time.PosixTimeInMicroseconds(
          timestamp=time_value[0])
      event = time_events.DateTimeValuesEvent(
          date_time, eventdata.EventTimestamp.CREATION_TIME)
      parser_mediator.ProduceEventWithEventData(event, event_data)

    time_value = time_dict.get(u'date-time-at-processing', None)
    if time_value is not None:
      date_time = dfdatetime_posix_time.PosixTimeInMicroseconds(
          timestamp=time_value[0])
      event = time_events.DateTimeValuesEvent(
          date_time, eventdata.EventTimestamp.START_TIME)
      parser_mediator.ProduceEventWithEventData(event, event_data)

    time_value = time_dict.get(u'date-time-at-completed', None)
    if time_value is not None:
      date_time = dfdatetime_posix_time.PosixTimeInMicroseconds(
          timestamp=time_value[0])
      event = time_events.DateTimeValuesEvent(
          date_time, eventdata.EventTimestamp.END_TIME)
      parser_mediator.ProduceEventWithEventData(event, event_data)

    time_value = time_dict.get(u'time-at-creation', None)
    if time_value is not None:
      date_time = dfdatetime_posix_time.PosixTime(timestamp=time_value[0])
      event = time_events.DateTimeValuesEvent(
          date_time, eventdata.EventTimestamp.CREATION_TIME)
      parser_mediator.ProduceEventWithEventData(event, event_data)

    time_value = time_dict.get(u'time-at-processing', None)
    if time_value is not None:
      date_time = dfdatetime_posix_time.PosixTime(timestamp=time_value[0])
      event = time_events.DateTimeValuesEvent(
          date_time, eventdata.EventTimestamp.START_TIME)
      parser_mediator.ProduceEventWithEventData(event, event_data)

    time_value = time_dict.get(u'time-at-completed', None)
    if time_value is not None:
      date_time = dfdatetime_posix_time.PosixTime(timestamp=time_value[0])
      event = time_events.DateTimeValuesEvent(
          date_time, eventdata.EventTimestamp.END_TIME)
      parser_mediator.ProduceEventWithEventData(event, event_data)