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

    data_dict = self._ReadPairs(parser_mediator, file_object)

    time_dict = {}

    for name in self._POSIX_TIME_VALUE_NAMES:
      value = data_dict.get(name, None)
      if value is not None:
        time_dict[name] = value
        del data_dict[name]

    event_data = CupsIppEventData()
    event_data.application = self._GetStringValue(data_dict, u'application')
    event_data.computer_name = self._GetStringValue(data_dict, u'computer_name')
    event_data.copies = data_dict.get(u'copies', [0])[0]
    event_data.data_dict = data_dict
    event_data.doc_type = self._GetStringValue(data_dict, u'doc_type')
    event_data.job_id = self._GetStringValue(data_dict, u'job_id')
    event_data.job_name = self._GetStringValue(data_dict, u'job_name')
    event_data.user = self._GetStringValue(data_dict, u'user')
    event_data.owner = self._GetStringValue(data_dict, u'owner')
    event_data.printer_id = self._GetStringValue(data_dict, u'printer_id')
    event_data.uri = self._GetStringValue(data_dict, u'uri')

    for name, usage in iter(self._POSIX_TIME_IN_MICROSECOND_VALUES.items()):
      time_values = time_dict.get(name, [])
      for time_value in time_values:
        date_time = dfdatetime_posix_time.PosixTimeInMicroseconds(
            timestamp=time_value)
        event = time_events.DateTimeValuesEvent(date_time, usage)
        parser_mediator.ProduceEventWithEventData(event, event_data)

    for name, usage in iter(self._POSIX_TIME_VALUES.items()):
      time_values = time_dict.get(name, [])
      for time_value in time_values:
        date_time = dfdatetime_posix_time.PosixTime(timestamp=time_value)
        event = time_events.DateTimeValuesEvent(date_time, usage)
        parser_mediator.ProduceEventWithEventData(event, event_data)